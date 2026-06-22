# 介绍

依赖安装,记得开虚拟环境装：
以miniconda为例子

```powershell
# 创建虚拟环境
conda create -n <虚拟环境名字> python=3.11 -y
# 进入虚拟环境
conda activate <虚拟环境名字> 
```

`python==3.11`
(CPU还是GPU二选一)
下面这个是cpu版本

- `pip install paddlepaddle==3.3.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/`

**GPU版本，用nvidia显卡的下这个(应该都是cu>12的吧) 不确定的去命令行输入**`smi-nvidia`**查看**

- `pip install paddlepaddle-gpu==3.3.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu129/`
下载ocr
- `pip install paddleocr`

# python脚本

CPU版本：

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False, 
    use_doc_unwarping=False, 
    use_textline_orientation=False, 
    enable_mkldnn=False,
)
result = ocr.predict("图片路径")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")
```

GPU版本

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False, 
    device="gpu", 
)
result = ocr.predict("图片路径")
for res in result:
    res.save_to_img("output") #不要看图可以删掉这行
    res.save_to_json("output") #json核心
```

运行脚本

```powershell
# 确保你当前处于对应的虚拟环境下,xxx为你的python文件名字
python xxx.py
```

