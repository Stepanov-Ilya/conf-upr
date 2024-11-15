import os
import subprocess
import argparse
import unittest


def get_commit_graph(repo_path, branch_name):
    """Получает граф коммитов для указанной ветки в формате (commit_hash, parent_hash)."""
    # Команда для получения хешей коммитов и их родителей
    cmd = ["git", "-C", repo_path, "log", branch_name, "--pretty=format:%H %P"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result)
        raise Exception("Ошибка при выполнении команды git log.")

    commit_graph = []
    for line in result.stdout.splitlines():
        parts = line.split()
        commit_hash = parts[0]
        parent_hashes = parts[1:]
        for parent in parent_hashes:
            commit_graph.append((parent, commit_hash))  # Каждый коммит связан со своими родителями

    return commit_graph


def generate_mermaid(commit_graph):
    """Генерация кода Mermaid для графа зависимостей."""
    lines = ["graph TD"]
    for parent, commit in commit_graph:
        lines.append(f'  {parent} --> {commit}')
    return "\n".join(lines)


def save_to_file(file_path, content):
    """Сохраняет контент в файл."""
    with open(file_path, "w") as file:
        file.write(content)


def visualize_with_mermaid(mermaid_path, output_file, output_image_path):
    """Визуализация графа с помощью внешней программы Mermaid."""
    cmd = [mermaid_path, "-i", output_file, "-o", output_image_path]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("Mermaid stderr:", result.stderr)  # Добавляем вывод ошибок
        raise Exception("Ошибка при выполнении Mermaid.")
    print(f"Граф успешно визуализирован. Результат сохранен в {output_image_path}.")



def main():
    parser = argparse.ArgumentParser(description="Инструмент для визуализации графа зависимостей коммитов Git.")
    parser.add_argument("--mermaid_path", required=True, help="Путь к программе для визуализации графов.")
    parser.add_argument("--repo_path", required=True, help="Путь к анализируемому git-репозиторию.")
    parser.add_argument("--output_image_path", required=True, help="Путь к файлу с изображением графа.")
    parser.add_argument("--branch_name", required=True, help="Имя ветки в репозитории.")
    args = parser.parse_args()

    output_file = "output.mmd"

    # Проверка существования репозитория
    if not os.path.isdir(os.path.join(args.repo_path, ".git")):
        print(f"Указанный путь {args.repo_path} не является git-репозиторием.")
        return

    try:
        # Получение графа зависимостей
        commit_graph = get_commit_graph(args.repo_path, args.branch_name)

        # Генерация Mermaid-кода
        mermaid_code = generate_mermaid(commit_graph)

        # Сохранение результата в файл
        save_to_file(output_file, mermaid_code)

        # Визуализация графа с помощью Mermaid и сохранение изображения
        visualize_with_mermaid(args.mermaid_path, output_file, args.output_image_path)

    except Exception as e:
        print(f"Ошибка: {e}")




if __name__ == "__main__":
    main()
