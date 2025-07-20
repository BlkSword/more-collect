#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import difflib
import os

class TextComparator:
    def __init__(self, root):
        self.root = root
        self.root.title("字典比对工具")
        
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        tk.Entry(top_frame, textvariable=self.file1_path).pack(padx=5, side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(top_frame, text="文件1", command=lambda: self.select_file(1)).pack(padx=10, side=tk.LEFT)
        
        tk.Entry(top_frame, textvariable=self.file2_path).pack(padx=5, side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(top_frame, text="文件2", command=lambda: self.select_file(2)).pack(padx=10, side=tk.LEFT)
        
        tk.Button(self.root, text="开始比对", command=self.compare_text).pack(pady=10, fill=tk.X, padx=5)
        
        # 结果显示框架
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        nav_frame = tk.Frame(result_frame)
        nav_frame.pack(side=tk.TOP, anchor=tk.E, padx=5, pady=5)
        
        tk.Button(nav_frame, text="上一个", command=self.prev_diff_block).pack(padx=5, side=tk.LEFT)
        tk.Button(nav_frame, text="下一个", command=self.next_diff_block).pack(padx=5, side=tk.LEFT)
        
        self.line_numbers = tk.Text(result_frame, width=4, padx=3, takefocus=0, border=0,
                                background="lightgray", state="disabled")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        self.result_text = tk.Text(result_frame, height=30)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(result_frame, command=self.sync_scroll)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        tk.Button(self.root, text="保存结果", command=self.save_result).pack(pady=5, fill=tk.X, padx=5)
        tk.Button(self.root, text="保存合并文件", command=self.save_merged_result).pack(pady=5, fill=tk.X, padx=5)
        
        self.result_text.tag_config('added', background='lightgreen')
        self.result_text.tag_config('removed', background='lightcoral')
        
    def select_file(self, file_num):
        file_path = filedialog.askopenfilename()
        if file_path:
            if file_num == 1:
                self.file1_path.set(file_path)
            else:
                self.file2_path.set(file_path)
                
    def sync_scroll(self, *args):
        self.result_text.yview(*args)
        self.line_numbers.yview(*args)
        
    def update_line_numbers(self, event=None):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        
        line_count = int(self.result_text.index(tk.END).split('.')[0]) - 1
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
            
        self.line_numbers.config(state="disabled")
        
    def compare_text(self):
        try:
            with open(self.file1_path.get(), 'r', encoding='utf-8') as f1:
                text1 = f1.read().splitlines()
                
            with open(self.file2_path.get(), 'r', encoding='utf-8') as f2:
                text2 = f2.read().splitlines()
                
            d = difflib.Differ()
            diff = list(d.compare(text1, text2))
            
            self.result_text.delete(1.0, tk.END)
            self.update_line_numbers()
            
            self.diff_lines = []
            self.current_diff_index = -1  
            
            self.diff_blocks = []  
            self.current_block_index = -1  
            
            for line in diff:
                if line.startswith('+ '):
                    tag = 'added'
                    self.result_text.insert(tk.END, line + '\n', tag)
                    self.diff_lines.append((tag, line))
                elif line.startswith('- '):
                    tag = 'removed'
                    self.result_text.insert(tk.END, line + '\n', tag)
                    self.diff_lines.append((tag, line))
                else:
                    self.result_text.insert(tk.END, line + '\n')
                    self.diff_lines.append((None, line))
                    
            self.result_text.bind("<KeyRelease>", self.update_line_numbers)
            self.result_text.bind("<ButtonRelease-1>", self.update_line_numbers)
            
            current_block = None
            for i, (tag, line) in enumerate(self.diff_lines):
                if tag in ['added', 'removed']:
                    if current_block is None:
                        current_block = {'type': tag, 'start': i, 'end': i}
                    else:
                        current_block['end'] = i
                else:
                    if current_block:
                        self.diff_blocks.append(current_block)
                        current_block = None
            
            if current_block:
                self.diff_blocks.append(current_block)
                
            if self.diff_blocks:
                self.current_block_index = 0
                self.highlight_diff_block(self.diff_blocks[0])
                line_number = self.diff_blocks[0]['start'] + 1
                self.result_text.see(f"{line_number}.0")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件时出错: {e}")

    def prev_diff_block(self):
        if not hasattr(self, 'diff_blocks') or not self.diff_blocks:
            return
            
        start_index = self.current_block_index - 1
        if start_index >= 0:
            self.current_block_index = start_index
            block = self.diff_blocks[self.current_block_index]
            line_number = block['start'] + 1
            self.result_text.see(f"{line_number}.0")
            self.result_text.tag_add("sel", f"{line_number}.0", f"{block['end']+1}.end+1c")
            self.result_text.focus_set()
            self.highlight_diff_block(block)
        elif self.diff_blocks:  
            self.current_block_index = 0
            block = self.diff_blocks[0]
            line_number = block['start'] + 1
            self.result_text.see(f"{line_number}.0")
            self.result_text.tag_add("sel", f"{line_number}.0", f"{block['end']+1}.end+1c")
            self.result_text.focus_set()
            self.highlight_diff_block(block)

    def next_diff_block(self):
        if not hasattr(self, 'diff_blocks') or not self.diff_blocks:
            return
            
        start_index = self.current_block_index + 1
        if start_index < len(self.diff_blocks):
            self.current_block_index = start_index
            block = self.diff_blocks[self.current_block_index]
            line_number = block['start'] + 1
            self.result_text.see(f"{line_number}.0")
            self.result_text.tag_add("sel", f"{line_number}.0", f"{block['end']+1}.end+1c")
            self.result_text.focus_set()
            self.highlight_diff_block(block)
        elif self.diff_blocks: 
            self.current_block_index = len(self.diff_blocks) - 1
            block = self.diff_blocks[-1]
            line_number = block['start'] + 1
            self.result_text.see(f"{line_number}.0")
            self.result_text.tag_add("sel", f"{line_number}.0", f"{block['end']+1}.end+1c")
            self.result_text.focus_set()
            self.highlight_diff_block(block)

    def save_result(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("文本文件", "*.txt")])
        if output_path:
            try:
                result_content = self.result_text.get(1.0, tk.END)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result_content)
                    
                messagebox.showinfo("成功", f"结果已保存到:\n{output_path}")
                
            except Exception as e:
                messagebox.showerror("错误", f"保存文件时出错: {e}")

    def save_merged_result(self):
        output_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                        filetypes=[("文本文件", "*.txt")])
        if not output_path:
            return

        try:
            merged_lines = []
            for tag, line in self.diff_lines:
                if tag in ['added', 'removed']:
                    choice = messagebox.askyesno(
                        "选择差异行",
                        f"是否保留以下变更行？\n\n{line}\n\n(是：保留  否：舍弃)",
                        default=messagebox.YES
                    )
                    if choice:
                        merged_lines.append(line)
                else:
                    merged_lines.append(line)
                    
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(merged_lines) + '\n')
                
            messagebox.showinfo("成功", f"合并结果已保存到:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存文件时出错: {e}")

    def highlight_diff_block(self, block):
        """高亮显示差异块"""
        self.result_text.tag_remove("sel", 1.0, tk.END)  
        start_line = block['start'] + 1
        end_line = block['end'] + 1
        self.result_text.tag_add("highlight", f"{start_line}.0", f"{end_line}.end+1c")
        self.result_text.tag_config("highlight")  

if __name__ == "__main__":
    root = tk.Tk()
    app = TextComparator(root)
    root.mainloop()