# VietCardLib

Thư viện xử lý ORB, tiền xử lý và OCR giấy tờ tùy thân Việt Nam.

## 📋 Tính năng

- **ORB Image Alignment**: Căn chỉnh ảnh giấy tờ tùy thân sử dụng ORB features
- **Size Normalization**: Tự động chuẩn hóa kích thước ảnh trước khi xử lý
- **Validation System**: Hệ thống kiểm tra chất lượng để tránh false positives
- **Multi-scale Processing**: Xử lý ảnh ở nhiều tỷ lệ khác nhau

## 🚀 Cài đặt

```bash
pip install VietCardLib
```

Hoặc cài đặt từ source:

```bash
git clone https://github.com/doanngocthanh/VietCardLib.git
cd VietCardLib
pip install -e .
```

## 📖 Sử dụng

### ORB Image Alignment

```python
from VietCardLib import ORBImageAligner

# Khởi tạo aligner
aligner = ORBImageAligner(target_dimension=800, orb_features=2000)

# Thực hiện alignment
result = aligner.align_images(
    base_image_path="path/to/base_image.jpg",
    target_image_path="path/to/target_image.jpg",
    output_path="path/to/output.jpg"
)

if result["success"]:
    print(f"Alignment thành công! Quality: {result['quality_score']:.3f}")
    print(f"Ảnh đã căn chỉnh: {result['aligned_image_path']}")
else:
    print(f"Alignment thất bại: {result['error']}")
```

### Batch Processing

```python
# Căn chỉnh nhiều ảnh cùng lúc
results = aligner.batch_align(
    base_image_path="base.jpg",
    target_directory="input_images/",
    output_directory="aligned_images/"
)

for result in results:
    if result["success"]:
        print(f"✅ {result['filename']}: Quality {result['quality_score']:.3f}")
    else:
        print(f"❌ {result['filename']}: {result['error']}")
```

## 🔧 Tham số

### ORBImageAligner

- `target_dimension` (int): Kích thước chuẩn để normalize ảnh (default: 800)
- `orb_features` (int): Số lượng ORB features tối đa (default: 2000)
- `min_matches` (int): Số lượng matches tối thiểu (default: 15)
- `min_inlier_ratio` (float): Tỷ lệ inliers tối thiểu (default: 0.3)
- `quality_threshold` (float): Ngưỡng chất lượng tối thiểu (default: 0.3)

## 📊 Validation System

Thư viện tích hợp hệ thống validation để đảm bảo chất lượng:

- **Inlier Ratio Check**: Kiểm tra tỷ lệ inliers/matches
- **Quality Score**: Đánh giá dựa trên NCC, SSIM, edge similarity
- **Feature Count**: Kiểm tra số lượng features và matches
- **Robustness Test**: Thử nghiệm với nhiều tham số RANSAC

## 🎯 Ứng dụng

- Căn chỉnh CCCD/CMND để chuẩn bị cho OCR
- Preprocessing ảnh giấy tờ tùy thân
- Chuẩn hóa ảnh documents
- Template matching cho form processing

## 📋 Yêu cầu hệ thống

- Python >= 3.6
- OpenCV >= 4.0
- NumPy >= 1.18
- Matplotlib >= 3.0 (optional, cho visualization)

## 📄 License

MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.

## 🚀 Development & Deploy

### Local Development

```bash
# Clone repository
git clone https://github.com/doanngocthanh/VietCardLib.git
cd VietCardLib

# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Run example
python examples/basic_alignment.py
```

### Building and Deploy

```bash
# Install build dependencies
pip install build twine wheel

# Build package
python -m build

# Check package
python -m twine check dist/*

# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

Hoặc sử dụng script tự động:

```bash
# Chạy deploy script
python deploy.py

# Chọn option:
# 1. Build only
# 2. Build and check  
# 3. Build and upload to Test PyPI
# 4. Build and upload to PyPI
# 5. Clean build artifacts
```

### Deployment Checklist

- [ ] Cập nhật version trong `setup.py` và `__init__.py`
- [ ] Cập nhật CHANGELOG.md
- [ ] Test toàn bộ functionality
- [ ] Chạy `python deploy.py` option 2 để build và check
- [ ] Upload to Test PyPI để test (option 3)
- [ ] Test install từ Test PyPI: `pip install -i https://test.pypi.org/simple/ VietCardLib`
- [ ] Upload to PyPI chính thức (option 4)

## 👥 Contributing

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📧 Contact

Đoàn Ngọc Thành - dnt.doanngocthanh@gmail.com

Project Link: [https://github.com/doanngocthanh/VietCardLib](https://github.com/doanngocthanh/VietCardLib)

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## 👨‍💻 Tác giả

**Đoàn Ngọc Thành**
- Email: dnt.doanngocthanh@gmail.com
- GitHub: [@doanngocthanh](https://github.com/doanngocthanh)

## 🤝 Đóng góp

Chào mừng mọi đóng góp! Vui lòng đọc [CONTRIBUTING.md](CONTRIBUTING.md) để biết thêm chi tiết.

## 📝 Changelog

### v0.1.0 (2025-09-09)
- Phiên bản đầu tiên
- ORB Image Alignment với size normalization
- Validation system để tránh false positives
- Batch processing support