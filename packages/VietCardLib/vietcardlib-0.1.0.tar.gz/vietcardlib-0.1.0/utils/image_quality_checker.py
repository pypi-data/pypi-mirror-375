import cv2
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

class ImageQualityChecker:
    """
    Class kiểm tra chất lượng ảnh templates, đảm bảo cùng tỷ lệ và chất lượng tốt
    """
    
    def __init__(self, base_template_path: str = None):
        """
        Khởi tạo checker với base template
        
        Args:
            base_template_path: Đường dẫn ảnh template chuẩn
        """
        self.base_template_path = base_template_path
        self.base_specs = None
        
        if base_template_path and os.path.exists(base_template_path):
            self.base_specs = self._analyze_image(base_template_path)
            print(f"📋 Base template loaded: {os.path.basename(base_template_path)}")
            print(f"   Size: {self.base_specs['dimensions']}")
            print(f"   Aspect ratio: {self.base_specs['aspect_ratio']:.3f}")
            print(f"   Quality score: {self.base_specs['quality_score']:.3f}")
    
    def _analyze_image(self, image_path: str) -> Dict:
        """
        Phân tích chi tiết một ảnh
        
        Args:
            image_path: Đường dẫn ảnh
            
        Returns:
            Dict chứa thông tin chi tiết ảnh
        """
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Cannot read image"}
            
            # Basic info
            height, width, channels = image.shape
            file_size = os.path.getsize(image_path)
            
            # Aspect ratio
            aspect_ratio = width / height
            
            # Convert to grayscale cho analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness (Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Contrast (standard deviation)
            contrast = np.std(gray)
            
            # Brightness (mean value)
            brightness = np.mean(gray)
            
            # Edge density
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # Noise estimation (using high-frequency components)
            kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]])
            noise_estimate = np.std(cv2.filter2D(gray, -1, kernel))
            
            # Overall quality score
            quality_score = self._calculate_quality_score(
                laplacian_var, contrast, brightness, edge_density, noise_estimate
            )
            
            # Color analysis
            color_channels = cv2.split(image)
            color_balance = {
                'blue_mean': np.mean(color_channels[0]),
                'green_mean': np.mean(color_channels[1]), 
                'red_mean': np.mean(color_channels[2])
            }
            
            # Histogram analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_entropy = -np.sum(hist * np.log2(hist + 1e-10))
            
            return {
                'filename': os.path.basename(image_path),
                'dimensions': (width, height),
                'channels': channels,
                'file_size_mb': file_size / (1024 * 1024),
                'aspect_ratio': aspect_ratio,
                'sharpness': laplacian_var,
                'contrast': contrast,
                'brightness': brightness,
                'edge_density': edge_density,
                'noise_estimate': noise_estimate,
                'quality_score': quality_score,
                'color_balance': color_balance,
                'histogram_entropy': hist_entropy,
                'pixel_count': width * height
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _calculate_quality_score(self, sharpness: float, contrast: float, 
                                brightness: float, edge_density: float, 
                                noise: float) -> float:
        """
        Tính điểm chất lượng tổng hợp
        
        Args:
            sharpness: Độ sắc nét (Laplacian variance)
            contrast: Độ tương phản
            brightness: Độ sáng
            edge_density: Mật độ edge
            noise: Ước lượng noise
            
        Returns:
            Quality score từ 0-1
        """
        # Normalize các metrics
        # Sharpness: > 100 is good
        sharpness_score = min(sharpness / 200.0, 1.0)
        
        # Contrast: 40-80 is good range
        contrast_score = 1.0 - abs(contrast - 60) / 60.0
        contrast_score = max(0, contrast_score)
        
        # Brightness: 80-180 is good range
        brightness_score = 1.0 - abs(brightness - 130) / 130.0
        brightness_score = max(0, brightness_score)
        
        # Edge density: 0.02-0.15 is good range
        edge_score = min(edge_density / 0.1, 1.0) if edge_density > 0.01 else 0
        
        # Noise: lower is better
        noise_score = max(0, 1.0 - noise / 50.0)
        
        # Weighted combination
        quality = (0.3 * sharpness_score + 
                  0.2 * contrast_score + 
                  0.15 * brightness_score + 
                  0.2 * edge_score + 
                  0.15 * noise_score)
        
        return min(1.0, max(0.0, quality))
    
    def check_aspect_ratio_compatibility(self, image_specs: Dict, 
                                       tolerance: float = 0.05) -> Dict:
        """
        Kiểm tra tỷ lệ khung hình có tương thích với base template không
        
        Args:
            image_specs: Thông số ảnh cần kiểm tra
            tolerance: Dung sai cho aspect ratio (default: 5%)
            
        Returns:
            Dict kết quả kiểm tra
        """
        if not self.base_specs:
            return {"compatible": False, "reason": "No base template set"}
        
        if "error" in image_specs:
            return {"compatible": False, "reason": image_specs["error"]}
        
        base_ratio = self.base_specs['aspect_ratio']
        image_ratio = image_specs['aspect_ratio']
        
        ratio_diff = abs(base_ratio - image_ratio) / base_ratio
        
        is_compatible = ratio_diff <= tolerance
        
        return {
            "compatible": is_compatible,
            "base_ratio": base_ratio,
            "image_ratio": image_ratio,
            "difference": ratio_diff,
            "tolerance": tolerance,
            "recommendation": self._get_ratio_recommendation(ratio_diff, tolerance)
        }
    
    def _get_ratio_recommendation(self, ratio_diff: float, tolerance: float) -> str:
        """Đưa ra khuyến nghị về aspect ratio"""
        if ratio_diff <= tolerance:
            return "✅ Tỷ lệ khung hình phù hợp"
        elif ratio_diff <= tolerance * 2:
            return "⚠️ Tỷ lệ khung hình hơi khác, có thể cần điều chỉnh"
        else:
            return "❌ Tỷ lệ khung hình khác nhiều, cần resize"
    
    def check_image_quality(self, image_specs: Dict, 
                          min_quality: float = 0.5) -> Dict:
        """
        Kiểm tra chất lượng ảnh
        
        Args:
            image_specs: Thông số ảnh
            min_quality: Chất lượng tối thiểu
            
        Returns:
            Dict kết quả kiểm tra chất lượng
        """
        if "error" in image_specs:
            return {"quality_ok": False, "reason": image_specs["error"]}
        
        quality_score = image_specs['quality_score']
        quality_ok = quality_score >= min_quality
        
        # Chi tiết các metrics
        issues = []
        recommendations = []
        
        # Check sharpness
        if image_specs['sharpness'] < 50:
            issues.append("Ảnh không đủ sắc nét")
            recommendations.append("Cần ảnh có độ phân giải cao hơn hoặc focus tốt hơn")
        
        # Check contrast
        if image_specs['contrast'] < 30:
            issues.append("Độ tương phản thấp")
            recommendations.append("Tăng contrast trong post-processing")
        elif image_specs['contrast'] > 100:
            issues.append("Độ tương phản quá cao")
            recommendations.append("Giảm contrast, tránh overexposure")
        
        # Check brightness
        if image_specs['brightness'] < 60:
            issues.append("Ảnh quá tối")
            recommendations.append("Tăng độ sáng hoặc cải thiện lighting")
        elif image_specs['brightness'] > 200:
            issues.append("Ảnh quá sáng")
            recommendations.append("Giảm exposure, tránh blown highlights")
        
        # Check noise
        if image_specs['noise_estimate'] > 30:
            issues.append("Noise cao")
            recommendations.append("Sử dụng noise reduction hoặc chụp ở ISO thấp hơn")
        
        return {
            "quality_ok": quality_ok,
            "quality_score": quality_score,
            "min_quality": min_quality,
            "issues": issues,
            "recommendations": recommendations,
            "grade": self._get_quality_grade(quality_score)
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Đánh giá grade cho quality score"""
        if score >= 0.8:
            return "A - Xuất sắc"
        elif score >= 0.6:
            return "B - Tốt"
        elif score >= 0.4:
            return "C - Khá"
        elif score >= 0.2:
            return "D - Yếu"
        else:
            return "F - Rất kém"
    
    def check_template_directory(self, template_dir: str, 
                               output_report: str = None) -> Dict:
        """
        Kiểm tra toàn bộ thư mục templates
        
        Args:
            template_dir: Đường dẫn thư mục templates
            output_report: File để lưu báo cáo (optional)
            
        Returns:
            Dict báo cáo tổng hợp
        """
        print(f"🔍 Đang kiểm tra thư mục: {template_dir}")
        
        # Tìm tất cả file ảnh
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(os.path.join(root, file))
        
        print(f"📋 Tìm thấy {len(image_files)} file ảnh")
        
        # Phân tích từng ảnh
        results = []
        summary = {
            "total_images": len(image_files),
            "quality_passed": 0,
            "ratio_compatible": 0,
            "issues_found": [],
            "recommendations": []
        }
        
        for i, image_path in enumerate(image_files, 1):
            print(f"   📸 ({i}/{len(image_files)}) {os.path.basename(image_path)}")
            
            # Analyze image
            specs = self._analyze_image(image_path)
            
            if "error" in specs:
                result = {
                    "file": image_path,
                    "status": "error",
                    "error": specs["error"]
                }
            else:
                # Check quality
                quality_check = self.check_image_quality(specs)
                
                # Check aspect ratio if base template is set
                ratio_check = None
                if self.base_specs:
                    ratio_check = self.check_aspect_ratio_compatibility(specs)
                
                result = {
                    "file": image_path,
                    "status": "analyzed",
                    "specs": specs,
                    "quality_check": quality_check,
                    "ratio_check": ratio_check
                }
                
                # Update summary
                if quality_check["quality_ok"]:
                    summary["quality_passed"] += 1
                
                if ratio_check and ratio_check["compatible"]:
                    summary["ratio_compatible"] += 1
                
                # Collect issues
                if quality_check["issues"]:
                    summary["issues_found"].extend(quality_check["issues"])
                
                if quality_check["recommendations"]:
                    summary["recommendations"].extend(quality_check["recommendations"])
            
            results.append(result)
        
        # Generate final report
        report = {
            "timestamp": str(Path().absolute()),
            "base_template": self.base_template_path,
            "summary": summary,
            "detailed_results": results
        }
        
        # Save report if requested
        if output_report:
            with open(output_report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📄 Báo cáo đã lưu: {output_report}")
        
        return report
    
    def print_summary_report(self, report: Dict):
        """In báo cáo tóm tắt ra console"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("📊 BÁO CÁO KIỂM TRA CHẤT LƯỢNG TEMPLATES")
        print("="*60)
        
        print(f"📋 Tổng số ảnh: {summary['total_images']}")
        print(f"✅ Chất lượng đạt: {summary['quality_passed']}/{summary['total_images']} ({summary['quality_passed']/summary['total_images']*100:.1f}%)")
        
        if self.base_specs:
            print(f"📐 Tỷ lệ tương thích: {summary['ratio_compatible']}/{summary['total_images']} ({summary['ratio_compatible']/summary['total_images']*100:.1f}%)")
        
        # Chi tiết từng ảnh
        print(f"\n📋 Chi tiết từng ảnh:")
        for result in report["detailed_results"]:
            filename = os.path.basename(result["file"])
            
            if result["status"] == "error":
                print(f"   ❌ {filename}: {result['error']}")
            else:
                quality = result["quality_check"]
                ratio = result["ratio_check"]
                
                quality_icon = "✅" if quality["quality_ok"] else "❌"
                ratio_icon = "✅" if ratio and ratio["compatible"] else "❌" if ratio else "➖"
                
                print(f"   {quality_icon} {filename}")
                print(f"      Quality: {quality['grade']} ({quality['quality_score']:.3f})")
                
                if ratio:
                    print(f"      Ratio: {ratio['recommendation']}")
                
                if quality["issues"]:
                    for issue in quality["issues"]:
                        print(f"      ⚠️ {issue}")
        
        print("\n" + "="*60)

def main():
    """Demo usage"""
    # Đường dẫn base template
    base_template = r"C:\WorkSpace\DECDM\VietCardLib\templates\base\0_CANCUOC.jpg"
    
    # Khởi tạo checker
    checker = ImageQualityChecker(base_template_path=base_template)
    
    # Kiểm tra thư mục templates
    template_dir = r"C:\WorkSpace\DECDM\VietCardLib\templates"
    
    print("🚀 BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG TEMPLATES")
    print("="*60)
    
    # Chạy kiểm tra
    report = checker.check_template_directory(
        template_dir, 
        output_report="template_quality_report.json"
    )
    
    # In báo cáo
    checker.print_summary_report(report)
    
    print("\n💡 Khuyến nghị:")
    unique_recommendations = list(set(report["summary"]["recommendations"]))
    for rec in unique_recommendations[:5]:  # Top 5 recommendations
        print(f"   • {rec}")

if __name__ == "__main__":
    main()
