def count_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return sum(1 for _ in file)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("请提供文件路径参数")
    else:
        file_path = sys.argv[1]
        try:
            line_count = count_lines(file_path)
            print(f"文件 {file_path} 总行数: {line_count}")
        except FileNotFoundError:
            print("错误：文件未找到")
        except Exception as e:
            print(f"读取文件时出错: {e}")