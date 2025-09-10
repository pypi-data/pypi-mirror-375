import cv2
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

class ImageAutoAdjuster:
    """
    Class tự động điều chỉnh ảnh templates để đạt chất lượng tốt và tỷ lệ đồng nhất
    """
    
    def __init__(self, base_template_path: str):
        """
        Khởi tạo auto adjuster với base template
        
        Args:
            base_template_path: Đường dẫn ảnh template chuẩn
        """
        self.base_template_path = base_template_path
        self.base_specs = self._get_base_specs()
        
        print(f"📋 Base template: {os.path.basename(base_template_path)}")
        print(f"   Target size: {self.base_specs['dimensions']}")
        print(f"   Target ratio: {self.base_specs['aspect_ratio']:.3f}")
    
    def _get_base_specs(self) -> Dict:
        """Lấy thông số base template"""
        if not os.path.exists(self.base_template_path):
            raise FileNotFoundError(f"Base template not found: {self.base_template_path}")
        
        image = cv2.imread(self.base_template_path)
        height, width = image.shape[:2]
        aspect_ratio = width / height
        
        return {
            'dimensions': (width, height),
            'aspect_ratio': aspect_ratio,
            'width': width,
            'height': height
        }
    
    def auto_adjust_image(self, input_path: str, output_path: str = None) -> Dict:
        """
        Tự động điều chỉnh ảnh để phù hợp với base template
        
        Args:
            input_path: Đường dẫn ảnh đầu vào
            output_path: Đường dẫn ảnh đầu ra (None = auto generate)
            
        Returns:
            Dict kết quả điều chỉnh
        """
        try:
            # Đọc ảnh
            image = cv2.imread(input_path)
            if image is None:
                return {"success": False, "error": "Cannot read image"}
            
            original_shape = image.shape
            print(f"🔧 Adjusting: {os.path.basename(input_path)} {original_shape[:2]}")
            
            # Bước 1: Resize về đúng aspect ratio và kích thước
            adjusted_image = self._resize_to_target(image)
            print(f"   📏 Resized to: {adjusted_image.shape[:2]}")
            
            # Bước 2: Điều chỉnh brightness (giảm độ sáng vì hầu hết ảnh quá sáng)
            adjusted_image = self._adjust_brightness(adjusted_image, factor=0.85)
            print(f"   💡 Brightness adjusted")
            
            # Bước 3: Giảm noise
            adjusted_image = self._reduce_noise(adjusted_image)
            print(f"   🔇 Noise reduced")
            
            # Bước 4: Tăng sharpness nhẹ
            adjusted_image = self._enhance_sharpness(adjusted_image)
            print(f"   🔍 Sharpness enhanced")
            
            # Bước 5: Điều chỉnh contrast
            adjusted_image = self._adjust_contrast(adjusted_image, factor=1.1)
            print(f"   🎨 Contrast adjusted")
            
            # Tạo output path nếu chưa có
            if output_path is None:
                name, ext = os.path.splitext(input_path)
                output_path = f"{name}_adjusted{ext}"
            
            # Lưu ảnh
            cv2.imwrite(output_path, adjusted_image)
            
            # Tính quality score sau điều chỉnh
            quality_after = self._calculate_quality_score(adjusted_image)
            
            return {
                "success": True,
                "input_path": input_path,
                "output_path": output_path,
                "original_shape": original_shape,
                "adjusted_shape": adjusted_image.shape,
                "quality_score": quality_after,
                "adjustments_applied": [
                    "resize_to_target",
                    "brightness_adjustment", 
                    "noise_reduction",
                    "sharpness_enhancement",
                    "contrast_adjustment"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _resize_to_target(self, image: np.ndarray) -> np.ndarray:
        """Resize ảnh về đúng tỷ lệ và kích thước target"""
        target_width = self.base_specs['width']
        target_height = self.base_specs['height']
        
        # Resize về đúng kích thước target
        resized = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
        
        return resized
    
    def _adjust_brightness(self, image: np.ndarray, factor: float = 0.85) -> np.ndarray:
        """Điều chỉnh độ sáng"""
        # Convert to float để tránh overflow
        adjusted = image.astype(np.float32) * factor
        
        # Clip về range hợp lệ
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return adjusted
    
    def _reduce_noise(self, image: np.ndarray) -> np.ndarray:
        """Giảm noise sử dụng bilateral filter"""
        # Bilateral filter giữ edges sắc nét nhưng giảm noise
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        return denoised
    
    def _enhance_sharpness(self, image: np.ndarray) -> np.ndarray:
        """Tăng độ sắc nét nhẹ"""
        # Kernel cho sharpening
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1], 
                          [-1,-1,-1]])
        
        # Apply kernel nhẹ
        sharpened = cv2.filter2D(image, -1, kernel * 0.1)
        
        # Blend với ảnh gốc
        enhanced = cv2.addWeighted(image, 0.8, sharpened, 0.2, 0)
        
        return enhanced
    
    def _adjust_contrast(self, image: np.ndarray, factor: float = 1.1) -> np.ndarray:
        """Điều chỉnh contrast"""
        # Convert to float
        adjusted = image.astype(np.float32)
        
        # Apply contrast: new_pixel = (old_pixel - 128) * factor + 128
        adjusted = (adjusted - 128) * factor + 128
        
        # Clip về range hợp lệ
        adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
        
        return adjusted
    
    def _calculate_quality_score(self, image: np.ndarray) -> float:
        """Tính quality score cho ảnh"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 200.0, 1.0)
        
        # Contrast
        contrast = np.std(gray)
        contrast_score = max(0, 1.0 - abs(contrast - 60) / 60.0)
        
        # Brightness
        brightness = np.mean(gray)
        brightness_score = max(0, 1.0 - abs(brightness - 130) / 130.0)
        
        # Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])
        edge_score = min(edge_density / 0.1, 1.0) if edge_density > 0.01 else 0
        
        # Combined score
        quality = (0.3 * sharpness_score + 
                  0.25 * contrast_score + 
                  0.2 * brightness_score + 
                  0.25 * edge_score)
        
        return min(1.0, max(0.0, quality))
    
    def batch_adjust_directory(self, input_dir: str, output_dir: str = None) -> Dict:
        """
        Tự động điều chỉnh tất cả ảnh trong thư mục
        
        Args:
            input_dir: Thư mục đầu vào
            output_dir: Thư mục đầu ra (None = input_dir + "_adjusted")
            
        Returns:
            Dict báo cáo kết quả
        """
        print(f"🚀 Batch adjusting directory: {input_dir}")
        
        # Tạo output directory
        if output_dir is None:
            output_dir = f"{input_dir}_adjusted"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"📁 Created output directory: {output_dir}")
        
        # Tìm tất cả file ảnh
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    # Bỏ qua ảnh đã adjusted
                    if "_adjusted" not in file:
                        image_files.append(os.path.join(root, file))
        
        print(f"📋 Found {len(image_files)} images to adjust")
        
        # Điều chỉnh từng ảnh
        results = []
        success_count = 0
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n📸 ({i}/{len(image_files)}) Processing...")
            
            # Tạo output path
            rel_path = os.path.relpath(image_path, input_dir)
            name, ext = os.path.splitext(rel_path)
            output_path = os.path.join(output_dir, f"{name}_adjusted{ext}")
            
            # Tạo thư mục con nếu cần
            output_subdir = os.path.dirname(output_path)
            if not os.path.exists(output_subdir):
                os.makedirs(output_subdir)
            
            # Điều chỉnh ảnh
            result = self.auto_adjust_image(image_path, output_path)
            
            if result["success"]:
                success_count += 1
                print(f"   ✅ Success: Quality {result['quality_score']:.3f}")
            else:
                print(f"   ❌ Failed: {result['error']}")
            
            results.append(result)
        
        # Tóm tắt
        summary = {
            "total_images": len(image_files),
            "success_count": success_count,
            "failed_count": len(image_files) - success_count,
            "success_rate": success_count / len(image_files) * 100 if image_files else 0,
            "output_directory": output_dir
        }
        
        print(f"\n📊 Batch adjustment completed:")
        print(f"   ✅ Success: {success_count}/{len(image_files)} ({summary['success_rate']:.1f}%)")
        print(f"   📁 Output: {output_dir}")
        
        return {
            "summary": summary,
            "detailed_results": results
        }
    
    def compare_before_after(self, original_dir: str, adjusted_dir: str) -> Dict:
        """
        So sánh chất lượng trước và sau điều chỉnh
        
        Args:
            original_dir: Thư mục ảnh gốc
            adjusted_dir: Thư mục ảnh đã điều chỉnh
            
        Returns:
            Dict báo cáo so sánh
        """
        print(f"📊 Comparing before/after quality...")
        
        # Import ImageQualityChecker để so sánh
        from .image_quality_checker import ImageQualityChecker
        
        checker = ImageQualityChecker(self.base_template_path)
        
        # Kiểm tra ảnh gốc
        print(f"\n🔍 Analyzing original images...")
        original_report = checker.check_template_directory(original_dir)
        
        # Kiểm tra ảnh đã điều chỉnh
        print(f"\n🔍 Analyzing adjusted images...")
        adjusted_report = checker.check_template_directory(adjusted_dir)
        
        # So sánh
        orig_summary = original_report["summary"]
        adj_summary = adjusted_report["summary"]
        
        improvement = {
            "quality_improvement": adj_summary["quality_passed"] - orig_summary["quality_passed"],
            "ratio_improvement": adj_summary["ratio_compatible"] - orig_summary["ratio_compatible"],
            "quality_rate_before": orig_summary["quality_passed"] / orig_summary["total_images"] * 100,
            "quality_rate_after": adj_summary["quality_passed"] / adj_summary["total_images"] * 100,
            "ratio_rate_before": orig_summary["ratio_compatible"] / orig_summary["total_images"] * 100,
            "ratio_rate_after": adj_summary["ratio_compatible"] / adj_summary["total_images"] * 100
        }
        
        print(f"\n📈 IMPROVEMENT SUMMARY:")
        print(f"   Quality pass rate: {improvement['quality_rate_before']:.1f}% → {improvement['quality_rate_after']:.1f}%")
        print(f"   Ratio compatibility: {improvement['ratio_rate_before']:.1f}% → {improvement['ratio_rate_after']:.1f}%")
        
        return {
            "original_report": original_report,
            "adjusted_report": adjusted_report,
            "improvement": improvement
        }

def main():
    """Demo auto adjustment"""
    # Base template
    base_template = r"C:\WorkSpace\DECDM\VietCardLib\templates\base\0_CANCUOC.jpg"
    
    # Khởi tạo auto adjuster
    adjuster = ImageAutoAdjuster(base_template)
    
    # Auto adjust toàn bộ thư mục templates
    template_dir = r"C:\WorkSpace\DECDM\VietCardLib\templates"
    
    print("🚀 AUTO-ADJUSTING TEMPLATES")
    print("="*50)
    
    # Chạy batch adjustment
    batch_result = adjuster.batch_adjust_directory(template_dir)
    
    # So sánh trước và sau
    comparison = adjuster.compare_before_after(template_dir, batch_result["summary"]["output_directory"])
    
    print("\n🎉 Auto adjustment completed!")

if __name__ == "__main__":
    main()
