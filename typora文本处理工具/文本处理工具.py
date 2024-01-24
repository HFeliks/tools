import tkinter as tk
from tkinter import scrolledtext , ttk
import re


class TextProcessorApp:
    def __init__(self , master):
        self.master = master
        master.title("文本处理工具")

        self.choice_label = ttk.Label(master , text="选择处理类型:")
        self.choice_label.grid(row=0 , column=0 , pady=5)

        self.choice_var = tk.StringVar()
        self.choice_var.set("文本处理")
        self.choice_menu = ttk.Combobox(master , textvariable=self.choice_var ,
                                        values=["文本处理" , "转为脚注" , "图片标签处理"])
        self.choice_menu.grid(row=0 , column=1 , pady=5)

        self.input_label = ttk.Label(master , text="输入字符串:")
        self.input_label.grid(row=1 , column=0 , pady=5)

        self.input_textbox = scrolledtext.ScrolledText(master , wrap=tk.WORD , width=40 , height=10)
        self.input_textbox.grid(row=2 , column=0 , columnspan=2 , padx=10 , pady=5)

        self.paste_button = ttk.Button(master , text="粘贴" , command=self.paste_from_clipboard)
        self.paste_button.grid(row=2 , column=2 , pady=5)

        self.process_button = ttk.Button(master , text="处理" , command=self.process_text)
        self.process_button.grid(row=3 , column=0 , pady=5)

        self.output_label = ttk.Label(master , text="处理结果:")
        self.output_label.grid(row=4 , column=0 , pady=5)

        self.output_textbox = scrolledtext.ScrolledText(master , wrap=tk.WORD , width=40 , height=10 ,
                                                        state=tk.DISABLED)
        self.output_textbox.grid(row=5 , column=0 , columnspan=2 , padx=10 , pady=5)

        self.copy_button = ttk.Button(master , text="复制结果" , command=self.copy_to_clipboard)
        self.copy_button.grid(row=6 , column=0 , pady=5)

        self.clear_button = ttk.Button(master , text="清空" , command=self.clear_text)
        self.clear_button.grid(row=6 , column=1 , pady=5)

    def process_text(self):
        choice = self.choice_var.get()
        input_text = self.input_textbox.get("1.0" , 'end-1c')
        if choice == "文本处理":
            output_text = add_footnotes(input_text)
        elif choice == "转为脚注":
            output_text = convert_to_footnotes(input_text)
        elif choice == "图片标签处理":
            output_text = process_image_tag(input_text)
        else:
            output_text = "未选择有效的处理类型"
        self.output_textbox.config(state=tk.NORMAL)
        self.output_textbox.delete("1.0" , tk.END)
        self.output_textbox.insert(tk.END , output_text)
        self.output_textbox.config(state=tk.DISABLED)

    def copy_to_clipboard(self):
        result = self.output_textbox.get("1.0" , 'end-1c')
        self.master.clipboard_clear()
        self.master.clipboard_append(result)
        self.master.update()

    def clear_text(self):
        self.input_textbox.delete("1.0" , tk.END)
        self.output_textbox.config(state=tk.NORMAL)
        self.output_textbox.delete("1.0" , tk.END)
        self.output_textbox.config(state=tk.DISABLED)

    def paste_from_clipboard(self):
        clipboard_content = self.master.clipboard_get()
        self.input_textbox.delete(1.0 , tk.END)
        self.input_textbox.insert(tk.END , clipboard_content)


def add_footnotes(text):
    # 匹配[]-[]
    pattern1 = re.compile(r'\[(\d+)\]-\[(\d+)\]')

    def repl1(match):
        # 将多引用的数字拆分，包括范围内的数字，添加脚注
        # print(match)
        start_range = match.group(1)
        end_range = match.group(2) if match.group(2) else start_range
        # print(start_range,end_range)
        numbers = list(range(int(start_range) , int(end_range) + 1))

        footnotes = ''.join(f'[^{num}]' for num in numbers)
        return footnotes

    # 匹配类似[1,3-15]，[3]
    pattern2 = re.compile(r'\[(\d+)(?:\s*,\s*(\d+)(?:–(\d+))?)?\]')

    def repl2(match):
        # 提取匹配的结果
        footnotes = []
        # print('-----')
        # print(match)
        # print(match.group(1))
        # print(match.group(2))
        # print(match.group(3))
        # print('------')
        start_range = match.group(2) if match.group(2) else match.group(1)
        end_range = match.group(3) if match.group(3) else start_range
        if int(start_range) != int(end_range):
            numbers = list(range(int(start_range) , int(end_range) + 1))
            footnotes = ''.join(f'[^{num}]' for num in numbers)
            footnotes = '[^' + match.group(1) + ']' + footnotes
        else:
            footnotes = f'[^{start_range}]'
        return footnotes

    # #匹配类似[1,3,，6，15]，包括英文逗号和中文逗号
    pattern3 = re.compile(r'\[(\d+(?:\s*[,，]\s*\d+)*)\]')

    def repl3(match):
        # 将多引用的数字拆分，添加脚注
        numbers = [num.strip() for num in match.group(1).replace('，' , ',').split(',')]
        if len(numbers) == 1:
            return numbers[0]
        else:
            footnotes = ''.join(f'[^{num}]' for num in numbers)
            return footnotes

    result1 = re.sub(pattern1 , repl1 , text)
    result2 = re.sub(pattern2 , repl2 , result1)
    result = re.sub(pattern3 , repl3 , result2)
    return result


def convert_to_footnotes(text):
    references = text
    paragraphs = references.split('[')[1:]
    formatted_paragraphs = []

    for paragraph in paragraphs:
        # 在每段前加上 '[', 并将 '[n]' 替换为 '[^n]'
        formatted_paragraph = '[' + paragraph.replace('[' , '[^')
        formatted_paragraphs.append(formatted_paragraph)

    # 合并处理后的段落
    formatted_references = '\n'.join(formatted_paragraphs)
    pattern = re.compile(r'\[(\d+)\] ([^\[\n]+)')

    def repl(match):
        return f"[^{match.group(1)}]: {match.group(2)}"

    result = re.sub(pattern , repl , formatted_references)
    return result


def process_image_tag(input_string):
    # Check for the format ![image-xxxx](./path/to/image)
    match_format = re.search(r'!\[.*\]\((.*?)\)' , input_string)

    if match_format:
        img_path = match_format.group(1)
        img_path = img_path.replace(' ' , '%20')
        markdown_output = re.sub(r'(\[.*\]\()\s*(.*?)\s*(\))' , fr'\1{img_path}\3' , input_string)
        return markdown_output
    else:
        # Check for the format <img src="path/to/image">
        match = re.search(r'<img\s+src="(.*?)"' , input_string)

        if match:
            img_src = match.group(1)
            img_src = img_src.replace(' ' , '%20')
            markdown_output = f"![]({img_src})"
            return markdown_output
        else:
            return "未找到匹配的图像标签"


root = tk.Tk()
app = TextProcessorApp(root)
root.mainloop()
