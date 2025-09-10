"""
Smart ORB Image Aligner với CardInfo Integration
Tự động nhận diện loại thẻ và thực hiện alignment với template phù hợp
"""
import cv2
import numpy as np
import os
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Import CardInfo và ORBImageAligner
import sys
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from ..data.CardInfo import CardInfo, CardSide
from .ORBImageAligner import ORBImageAligner

class SmartORBAligner:
    """
    Smart ORB Aligner sử dụng CardInfo để tự động nhận diện và align thẻ
    """
    
    def __init__(self, target_dimension=800, orb_features=2000, base_templates_dir=None):
        """
        Khởi tạo Smart ORB Aligner
        
        Args:
            target_dimension: Kích thước chuẩn normalize
            orb_features: Số lượng ORB features
            base_templates_dir: Thư mục chứa base templates
        """
        self.target_dimension = target_dimension
        self.orb_features = orb_features
        
        # Khởi tạo CardInfo
        self.card_info = CardInfo()
        
        # Khởi tạo ORB aligner
        self.orb_aligner = ORBImageAligner(target_dimension, orb_features)
        
        # Base templates directory
        if base_templates_dir is None:
            self.base_templates_dir = os.path.join(parent_dir, "templates", "base")
        else:
            self.base_templates_dir = base_templates_dir
        
        # Load templates và tính chất lượng
        self.template_cache = {}
        self._load_templates()
        
        print(f"🎯 Smart ORB Aligner initialized")
        print(f"   ORB: {orb_features} features, {target_dimension}px target")
        print(f"   Templates: {len(self.template_cache)} loaded")
        print(f"   Base dir: {os.path.basename(self.base_templates_dir)}")
    
    def _load_templates(self):
        """Load và cache tất cả templates"""
        print(f"📂 Loading templates from CardInfo...")
        
        active_cards = self.card_info.get_active_cards()
        template_count = 0
        
        for card in active_cards:
            card_id = card["id"]
            card_name = card["name"]
            
            for side in card["sides"]:
                template_path = self.card_info.get_template_path(card_id, side)
                
                if template_path:
                    # Tạo full path
                    full_path = os.path.join(self.base_templates_dir, os.path.basename(template_path))
                    
                    # Thử các variations nếu file không tồn tại
                    if not os.path.exists(full_path):
                        # Thử tìm file tương tự trong thư mục
                        for file in os.listdir(self.base_templates_dir):
                            if (card["nameEn"].replace(" ", "").lower() in file.lower() or
                                str(card_id) in file):
                                full_path = os.path.join(self.base_templates_dir, file)
                                break
                    
                    if os.path.exists(full_path):
                        # Load template và tính chất lượng
                        template_image = cv2.imread(full_path)
                        if template_image is not None:
                            quality_score = self._calculate_template_quality(template_image)
                            
                            self.template_cache[f"{card_id}_{side}"] = {
                                "card_id": card_id,
                                "card_name": card_name,
                                "side": side,
                                "path": full_path,
                                "image": template_image,
                                "quality_score": quality_score,
                                "shape": template_image.shape
                            }
                            
                            template_count += 1
                            print(f"   ✅ {card_name} - {side}: {os.path.basename(full_path)} (Q: {quality_score:.3f})")
                        else:
                            print(f"   ❌ Cannot load: {full_path}")
                    else:
                        print(f"   ⚠️ Not found: {template_path}")
        
        print(f"📋 Loaded {template_count} templates from {len(active_cards)} card types")
    
    def _calculate_template_quality(self, image: np.ndarray) -> float:
        """Tính chất lượng template"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Sharpness
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness = min(laplacian_var / 200.0, 1.0)
        
        # Contrast
        contrast = np.std(gray) / 128.0
        contrast = min(contrast, 1.0)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
        edge_score = min(edge_density / 0.1, 1.0)
        
        # Combined quality
        quality = (0.4 * sharpness + 0.3 * contrast + 0.3 * edge_score)
        return min(1.0, max(0.0, quality))
    
    def detect_card_type(self, input_image_path: str, confidence_threshold: float = 0.3) -> Dict:
        """
        Tự động nhận diện loại thẻ bằng cách thử alignment với tất cả templates
        
        Args:
            input_image_path: Đường dẫn ảnh input
            confidence_threshold: Ngưỡng confidence tối thiểu
            
        Returns:
            Dict: Kết quả nhận diện với card_id, side, confidence
        """
        print(f"🔍 Auto-detecting card type for: {os.path.basename(input_image_path)}")
        
        if not os.path.exists(input_image_path):
            return {"success": False, "error": "Input image not found"}
        
        best_match = None
        best_score = 0.0
        all_results = []
        
        # Thử alignment với từng template
        for template_key, template_data in self.template_cache.items():
            try:
                print(f"   Testing: {template_data['card_name']} - {template_data['side']}")
                
                # Thực hiện alignment
                result = self.orb_aligner.align(
                    base_image_path=template_data['path'],
                    target_image_path=input_image_path
                )
                
                if result["success"]:
                    # Tính combined score từ quality và inlier ratio
                    alignment_score = result["quality_score"]
                    inlier_score = result["inlier_ratio"]
                    good_matches_score = min(result["good_matches"] / 100.0, 1.0)
                    
                    # Combined confidence score
                    combined_score = (0.4 * alignment_score + 
                                    0.35 * inlier_score + 
                                    0.25 * good_matches_score)
                    
                    print(f"      Quality: {alignment_score:.3f}, Inliers: {inlier_score:.3f}, Score: {combined_score:.3f}")
                    
                    result_info = {
                        "template_key": template_key,
                        "card_id": template_data["card_id"],
                        "card_name": template_data["card_name"],
                        "side": template_data["side"],
                        "confidence": combined_score,
                        "alignment_result": result
                    }
                    
                    all_results.append(result_info)
                    
                    # Cập nhật best match
                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = result_info
                else:
                    print(f"      ❌ Alignment failed: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
        
        # Kết quả
        if best_match and best_score >= confidence_threshold:
            print(f"\n🎯 BEST MATCH FOUND:")
            print(f"   Card: {best_match['card_name']}")
            print(f"   Side: {best_match['side']}")
            print(f"   Confidence: {best_match['confidence']:.3f}")
            
            return {
                "success": True,
                "detected_card_id": best_match["card_id"],
                "detected_card_name": best_match["card_name"],
                "detected_side": best_match["side"],
                "confidence": best_match["confidence"],
                "best_match": best_match,
                "all_results": all_results
            }
        else:
            print(f"\n❌ NO RELIABLE MATCH FOUND")
            print(f"   Best score: {best_score:.3f} (threshold: {confidence_threshold})")
            
            return {
                "success": False,
                "error": "No reliable card type detected",
                "best_score": best_score,
                "threshold": confidence_threshold,
                "all_results": all_results
            }
    
    def smart_align(self, input_image_path: str, output_path: str = None, 
                   auto_detect: bool = True, card_id: int = None, 
                   side: str = None) -> Dict:
        """
        Smart alignment: tự động nhận diện hoặc sử dụng card_id được chỉ định
        
        Args:
            input_image_path: Đường dẫn ảnh input
            output_path: Đường dẫn output
            auto_detect: Có tự động nhận diện không
            card_id: ID thẻ cụ thể (nếu không auto detect)
            side: Mặt thẻ cụ thể
            
        Returns:
            Dict: Kết quả alignment
        """
        print(f"🎯 SMART ALIGNMENT")
        print(f"   Input: {os.path.basename(input_image_path)}")
        print(f"   Auto detect: {auto_detect}")
        
        start_time = time.time()
        
        try:
            target_template = None
            detection_result = None
            
            if auto_detect:
                # Tự động nhận diện
                detection_result = self.detect_card_type(input_image_path)
                
                if detection_result["success"]:
                    card_id = detection_result["detected_card_id"]
                    side = detection_result["detected_side"]
                    target_template = detection_result["best_match"]["alignment_result"]
                    
                    print(f"✅ Auto-detected: {detection_result['detected_card_name']} - {side}")
                else:
                    return {
                        "success": False,
                        "error": "Auto detection failed",
                        "detection_result": detection_result,
                        "processing_time": time.time() - start_time
                    }
            else:
                # Sử dụng card_id và side được chỉ định
                if card_id is None or side is None:
                    return {
                        "success": False,
                        "error": "card_id and side must be specified when auto_detect=False",
                        "processing_time": time.time() - start_time
                    }
                
                # Tìm template tương ứng
                template_key = f"{card_id}_{side}"
                if template_key not in self.template_cache:
                    return {
                        "success": False,
                        "error": f"Template not found for card_id={card_id}, side={side}",
                        "processing_time": time.time() - start_time
                    }
                
                template_data = self.template_cache[template_key]
                print(f"📋 Using specified: {template_data['card_name']} - {side}")
                
                # Thực hiện alignment
                target_template = self.orb_aligner.align(
                    base_image_path=template_data['path'],
                    target_image_path=input_image_path,
                    output_path=output_path
                )
            
            # Kết quả cuối
            processing_time = time.time() - start_time
            
            if target_template and target_template["success"]:
                card_info = self.card_info.get_card_by_id(card_id)
                
                result = {
                    "success": True,
                    "card_id": card_id,
                    "card_name": card_info["name"] if card_info else "Unknown",
                    "side": side,
                    "aligned_image_path": target_template["aligned_image_path"],
                    "quality_score": target_template["quality_score"],
                    "good_matches": target_template["good_matches"],
                    "inliers": target_template["inliers"],
                    "inlier_ratio": target_template["inlier_ratio"],
                    "processing_time": processing_time,
                    "auto_detected": auto_detect,
                    "alignment_result": target_template
                }
                
                if detection_result:
                    result["detection_result"] = detection_result
                    result["confidence"] = detection_result.get("confidence", 0.0)
                
                return result
            else:
                return {
                    "success": False,
                    "error": target_template.get("error", "Alignment failed") if target_template else "Unknown error",
                    "processing_time": processing_time,
                    "detection_result": detection_result
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def batch_smart_align(self, image_list: List[str], output_dir: str = None) -> Dict:
        """
        Batch smart alignment cho nhiều ảnh
        
        Args:
            image_list: Danh sách đường dẫn ảnh
            output_dir: Thư mục output
            
        Returns:
            Dict: Báo cáo tổng hợp
        """
        print(f"🚀 BATCH SMART ALIGNMENT")
        print(f"   Processing {len(image_list)} images...")
        
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")
        
        results = []
        success_count = 0
        detection_stats = {}
        
        for i, image_path in enumerate(image_list, 1):
            print(f"\n📸 ({i}/{len(image_list)}) Processing: {os.path.basename(image_path)}")
            
            # Tạo output path
            output_path = None
            if output_dir:
                name, ext = os.path.splitext(os.path.basename(image_path))
                output_path = os.path.join(output_dir, f"{name}_aligned{ext}")
            
            # Smart alignment
            result = self.smart_align(image_path, output_path, auto_detect=True)
            
            if result["success"]:
                success_count += 1
                card_name = result["card_name"]
                
                # Thống kê detection
                if card_name not in detection_stats:
                    detection_stats[card_name] = 0
                detection_stats[card_name] += 1
                
                print(f"   ✅ Success: {card_name} - {result['side']}")
                print(f"      Quality: {result['quality_score']:.3f}")
                if result.get("confidence"):
                    print(f"      Confidence: {result['confidence']:.3f}")
            else:
                print(f"   ❌ Failed: {result['error']}")
            
            results.append(result)
        
        # Tóm tắt
        summary = {
            "total_images": len(image_list),
            "successful_alignments": success_count,
            "failed_alignments": len(image_list) - success_count,
            "success_rate": success_count / len(image_list) * 100 if image_list else 0,
            "detection_stats": detection_stats,
            "results": results
        }
        
        print(f"\n📊 BATCH ALIGNMENT SUMMARY:")
        print(f"   ✅ Success: {success_count}/{len(image_list)} ({summary['success_rate']:.1f}%)")
        
        if detection_stats:
            print(f"   📋 Detected card types:")
            for card_name, count in detection_stats.items():
                print(f"      {card_name}: {count}")
        
        return summary
    
    def get_available_templates(self) -> List[Dict]:
        """Lấy danh sách templates có sẵn"""
        templates = []
        for template_key, template_data in self.template_cache.items():
            templates.append({
                "card_id": template_data["card_id"],
                "card_name": template_data["card_name"],
                "side": template_data["side"],
                "template_path": template_data["path"],
                "quality_score": template_data["quality_score"],
                "shape": template_data["shape"]
            })
        return templates
    
    def print_available_templates(self):
        """In danh sách templates có sẵn"""
        templates = self.get_available_templates()
        
        print(f"\n📋 AVAILABLE TEMPLATES ({len(templates)}):")
        print("-" * 50)
        
        for template in templates:
            print(f"ID {template['card_id']}: {template['card_name']} - {template['side']}")
            print(f"   Path: {os.path.basename(template['template_path'])}")
            print(f"   Quality: {template['quality_score']:.3f}")
            print(f"   Size: {template['shape'][:2]}")
            print()
    
    def setCardInfo(self, new_card_info: CardInfo = None, templates_dir: str = None):
        """
        Cập nhật CardInfo và reload templates
        
        Args:
            new_card_info: CardInfo object mới (None = tạo mới)
            templates_dir: Thư mục templates mới (None = giữ nguyên)
        """
        print(f"🔄 Updating CardInfo and reloading templates...")
        
        # Cập nhật CardInfo
        if new_card_info is not None:
            self.card_info = new_card_info
            print(f"   ✅ CardInfo updated")
        else:
            # Tạo CardInfo mới
            self.card_info = CardInfo()
            print(f"   ✅ CardInfo recreated")
        
        # Cập nhật templates directory nếu có
        if templates_dir is not None:
            if os.path.exists(templates_dir):
                self.base_templates_dir = templates_dir
                print(f"   ✅ Templates directory updated: {templates_dir}")
            else:
                print(f"   ⚠️ Templates directory not found: {templates_dir}")
                print(f"   Keeping current: {self.base_templates_dir}")
        
        # Xóa cache cũ và reload templates
        self.template_cache.clear()
        self._load_templates()
        
        print(f"🎯 CardInfo update completed!")
        print(f"   Templates loaded: {len(self.template_cache)}")
        
        return len(self.template_cache)
    
    def addCustomTemplate(self, card_id: int, side: str, template_path: str, 
                         card_name: str = None) -> bool:
        """
        Thêm custom template vào cache mà không cần cập nhật CardInfo
        
        Args:
            card_id: ID thẻ
            side: Mặt thẻ (front/back)
            template_path: Đường dẫn template
            card_name: Tên thẻ (None = auto generate)
            
        Returns:
            bool: Thành công hay không
        """
        print(f"➕ Adding custom template: ID {card_id} - {side}")
        
        if not os.path.exists(template_path):
            print(f"   ❌ Template file not found: {template_path}")
            return False
        
        try:
            # Load template image
            template_image = cv2.imread(template_path)
            if template_image is None:
                print(f"   ❌ Cannot load image: {template_path}")
                return False
            
            # Tính quality score
            quality_score = self._calculate_template_quality(template_image)
            
            # Tạo card name nếu chưa có
            if card_name is None:
                card_name = f"Custom Card {card_id}"
            
            # Thêm vào cache
            template_key = f"{card_id}_{side}"
            self.template_cache[template_key] = {
                "card_id": card_id,
                "card_name": card_name,
                "side": side,
                "path": template_path,
                "image": template_image,
                "quality_score": quality_score,
                "shape": template_image.shape,
                "is_custom": True
            }
            
            print(f"   ✅ Custom template added: {card_name} - {side}")
            print(f"      Path: {os.path.basename(template_path)}")
            print(f"      Quality: {quality_score:.3f}")
            print(f"      Size: {template_image.shape[:2]}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error adding custom template: {str(e)}")
            return False
    
    def removeTemplate(self, card_id: int, side: str) -> bool:
        """
        Xóa template khỏi cache
        
        Args:
            card_id: ID thẻ
            side: Mặt thẻ
            
        Returns:
            bool: Thành công hay không
        """
        template_key = f"{card_id}_{side}"
        
        if template_key in self.template_cache:
            template_data = self.template_cache[template_key]
            del self.template_cache[template_key]
            
            print(f"🗑️ Removed template: {template_data['card_name']} - {side}")
            return True
        else:
            print(f"⚠️ Template not found: ID {card_id} - {side}")
            return False
    
    def updateTemplateQuality(self, card_id: int, side: str) -> Optional[float]:
        """
        Cập nhật lại quality score cho template
        
        Args:
            card_id: ID thẻ
            side: Mặt thẻ
            
        Returns:
            float: Quality score mới (None nếu không tìm thấy)
        """
        template_key = f"{card_id}_{side}"
        
        if template_key in self.template_cache:
            template_data = self.template_cache[template_key]
            
            # Tính lại quality
            new_quality = self._calculate_template_quality(template_data["image"])
            template_data["quality_score"] = new_quality
            
            print(f"🔄 Updated quality for {template_data['card_name']} - {side}: {new_quality:.3f}")
            return new_quality
        else:
            print(f"⚠️ Template not found: ID {card_id} - {side}")
            return None
    
    def optimizeTemplateCache(self, min_quality: float = 0.3):
        """
        Tối ưu template cache bằng cách loại bỏ templates chất lượng thấp
        
        Args:
            min_quality: Ngưỡng quality tối thiểu
        """
        print(f"🔧 Optimizing template cache (min quality: {min_quality})...")
        
        original_count = len(self.template_cache)
        removed_templates = []
        
        # Tìm templates chất lượng thấp
        keys_to_remove = []
        for template_key, template_data in self.template_cache.items():
            if template_data["quality_score"] < min_quality:
                keys_to_remove.append(template_key)
                removed_templates.append(f"{template_data['card_name']} - {template_data['side']} (Q: {template_data['quality_score']:.3f})")
        
        # Xóa khỏi cache
        for key in keys_to_remove:
            del self.template_cache[key]
        
        print(f"   ✅ Optimization completed:")
        print(f"      Original: {original_count} templates")
        print(f"      Removed: {len(removed_templates)} low-quality templates")
        print(f"      Remaining: {len(self.template_cache)} templates")
        
        if removed_templates:
            print(f"   🗑️ Removed templates:")
            for template in removed_templates:
                print(f"      - {template}")
        
        return len(self.template_cache)
    
def main():
    """Demo Smart ORB Aligner"""
    print("🎯 SMART ORB ALIGNER DEMO")
    print("="*50)
    
    # Khởi tạo Smart Aligner
    smart_aligner = SmartORBAligner(target_dimension=800, orb_features=1500)
    
    # Hiển thị templates có sẵn
    smart_aligner.print_available_templates()
    
    # Demo setCardInfo - reload templates
    print(f"\n🔄 DEMO: setCardInfo - Reloading templates...")
    template_count = smart_aligner.setCardInfo()
    print(f"Reloaded {template_count} templates")
    
    # Demo thêm custom template
    custom_template_path = r"C:\WorkSpace\DECDM\VietCardLib\templates\base\0_GPLX.jpg"
    if os.path.exists(custom_template_path):
        print(f"\n➕ DEMO: Adding custom template...")
        success = smart_aligner.addCustomTemplate(
            card_id=99, 
            side="front", 
            template_path=custom_template_path,
            card_name="Custom GPLX Template"
        )
        if success:
            print(f"   ✅ Custom template added successfully")
        
        # Hiển thị templates sau khi thêm
        print(f"\n📋 Templates after adding custom:")
        print(f"   Total: {len(smart_aligner.template_cache)}")
    
    # Demo tối ưu cache
    print(f"\n🔧 DEMO: Optimizing template cache...")
    remaining = smart_aligner.optimizeTemplateCache(min_quality=0.5)
    print(f"Templates remaining after optimization: {remaining}")
    
    # Test auto detection và alignment
    test_images = [
        r"C:\WorkSpace\DECDM\img\01HM00013263_img_2_a019d23c.png",
        r"C:\WorkSpace\DECDM\img\Screenshot 2025-09-09 115854.png"
    ]
    
    for test_img in test_images:
        if os.path.exists(test_img):
            print(f"\n🔍 TESTING AUTO DETECTION & ALIGNMENT:")
            print(f"Image: {os.path.basename(test_img)}")
            
            result = smart_aligner.smart_align(test_img, auto_detect=True)
            
            if result["success"]:
                print(f"✅ SUCCESS!")
                print(f"   Detected: {result['card_name']} - {result['side']}")
                print(f"   Quality: {result['quality_score']:.3f}")
                print(f"   Confidence: {result.get('confidence', 'N/A')}")
                print(f"   Processing time: {result['processing_time']:.2f}s")
                print(f"   Output: {result.get('aligned_image_path', 'N/A')}")
            else:
                print(f"❌ FAILED: {result['error']}")
                if result.get('best_score'):
                    print(f"   Best score: {result['best_score']:.3f}")
        else:
            print(f"⚠️ Test image not found: {test_img}")
    
    print(f"\n🎉 Smart ORB Aligner demo completed!")

if __name__ == "__main__":
    main()
