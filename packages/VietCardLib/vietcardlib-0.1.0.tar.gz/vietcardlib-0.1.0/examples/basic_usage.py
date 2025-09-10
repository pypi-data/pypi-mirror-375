"""
Ví dụ sử dụng VietCardLib để alignment ảnh CCCD
"""

from VietCardLib import ORBImageAligner
import os

def basic_alignment_example():
    """Ví dụ cơ bản về image alignment"""
    print("=== Ví dụ cơ bản - Image Alignment ===")
    
    # Khởi tạo aligner
    aligner = ORBImageAligner(target_dimension=800, orb_features=2000)
    
    # Đường dẫn ảnh (thay đổi theo ảnh thực tế của bạn)
    base_image_path = "base_cccd.jpg"
    target_image_path = "target_cccd.jpg"
    output_path = "aligned_cccd.jpg"
    
    # Kiểm tra file có tồn tại không
    if not os.path.exists(base_image_path):
        print(f"❌ Không tìm thấy file: {base_image_path}")
        return
    
    if not os.path.exists(target_image_path):
        print(f"❌ Không tìm thấy file: {target_image_path}")
        return
    
    # Thực hiện alignment
    print("🔄 Đang thực hiện alignment...")
    result = aligner.align_images(base_image_path, target_image_path, output_path)
    
    # Hiển thị kết quả
    if result["success"]:
        print("✅ Alignment thành công!")
        print(f"📄 Ảnh đã căn chỉnh: {result['aligned_image_path']}")
        print(f"🎯 Visualization: {result['visualization_path']}")
        print(f"📊 Comparison: {result['comparison_path']}")
        print(f"🔍 Quality Score: {result['quality_metrics']['overall_quality']:.3f}")
        print(f"🔗 Inliers: {result['inliers']}/{result['good_matches']} ({result['inlier_ratio']:.1%})")
        
        # Đánh giá chất lượng
        quality = result['quality_metrics']['overall_quality']
        if quality > 0.6:
            print("🎉 CHẤT LƯỢNG XUẤT SẮC!")
        elif quality > 0.4:
            print("👍 CHẤT LƯỢNG TỐT!")
        elif quality > 0.3:
            print("👌 Chất lượng khá")
        else:
            print("⚠️ Chất lượng thấp")
    else:
        print(f"❌ Alignment thất bại: {result['error']}")

def batch_alignment_example():
    """Ví dụ về batch alignment"""
    print("\n=== Ví dụ Batch Processing ===")
    
    # Khởi tạo aligner
    aligner = ORBImageAligner()
    
    # Đường dẫn
    base_image_path = "base_cccd.jpg"
    input_directory = "input_images/"
    output_directory = "aligned_images/"
    
    # Kiểm tra thư mục
    if not os.path.exists(input_directory):
        print(f"❌ Không tìm thấy thư mục: {input_directory}")
        return
    
    # Tạo thư mục output nếu chưa có
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"📁 Đã tạo thư mục: {output_directory}")
    
    # Thực hiện batch alignment
    print("🔄 Đang thực hiện batch alignment...")
    results = aligner.batch_align(base_image_path, input_directory, output_directory)
    
    # Thống kê kết quả
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"\n📊 Kết quả batch processing:")
    print(f"   Tổng số file: {total_count}")
    print(f"   Thành công: {success_count}")
    print(f"   Thất bại: {total_count - success_count}")
    print(f"   Tỷ lệ thành công: {success_count/total_count:.1%}" if total_count > 0 else "   Không có file nào")
    
    # Chi tiết từng file
    print(f"\n📋 Chi tiết:")
    for result in results:
        if result["success"]:
            quality = result['quality_metrics']['overall_quality']
            print(f"   ✅ {result['filename']}: Quality {quality:.3f}")
        else:
            print(f"   ❌ {result['filename']}: {result['error']}")

def advanced_configuration_example():
    """Ví dụ về cấu hình nâng cao"""
    print("\n=== Ví dụ Cấu hình Nâng cao ===")
    
    # Cấu hình cho ảnh chất lượng cao
    high_quality_aligner = ORBImageAligner(
        target_dimension=1200,  # Kích thước lớn hơn
        orb_features=5000,      # Nhiều features hơn
        min_matches=20,         # Yêu cầu nhiều matches hơn
        min_inlier_ratio=0.4,   # Tỷ lệ inliers cao hơn
        quality_threshold=0.4   # Chất lượng tối thiểu cao hơn
    )
    
    # Cấu hình cho ảnh chất lượng thấp
    fast_aligner = ORBImageAligner(
        target_dimension=600,   # Kích thước nhỏ hơn để xử lý nhanh
        orb_features=1000,      # Ít features hơn
        min_matches=8,          # Yêu cầu ít matches hơn
        min_inlier_ratio=0.2,   # Tỷ lệ inliers thấp hơn
        quality_threshold=0.2   # Chất lượng tối thiểu thấp hơn
    )
    
    print("🔧 Đã tạo 2 aligner với cấu hình khác nhau:")
    print("   - high_quality_aligner: Cho ảnh chất lượng cao")
    print("   - fast_aligner: Cho xử lý nhanh")

def main():
    """Chạy tất cả ví dụ"""
    print("🚀 VietCardLib Examples\n")
    
    try:
        basic_alignment_example()
        batch_alignment_example()
        advanced_configuration_example()
        
        print("\n✅ Hoàn thành tất cả ví dụ!")
        print("\n💡 Lưu ý:")
        print("   - Thay đổi đường dẫn ảnh phù hợp với môi trường của bạn")
        print("   - Điều chỉnh tham số aligner tùy theo chất lượng ảnh đầu vào")
        print("   - Kiểm tra quality score để đánh giá độ tin cậy")
        
    except Exception as e:
        print(f"❌ Lỗi khi chạy ví dụ: {e}")

if __name__ == "__main__":
    main()
