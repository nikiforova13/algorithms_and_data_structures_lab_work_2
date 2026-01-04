"""
Скрипт для анализа хеш-функции.
Генерирует ключи и анализирует распределение коллизий по сегментам.
"""

import random
import string
from collections import Counter
from app.hash_table import HashTable


def generate_key():
    """Генерирует случайный ключ формата цццБцц."""
    digits = string.digits
    letters = string.ascii_uppercase
    return (''.join(random.choice(digits) for _ in range(3)) +
            random.choice(letters) +
            ''.join(random.choice(digits) for _ in range(2)))


def analyze_hash_distribution(num_keys=7500):
    """
    Анализирует распределение хеш-функции.
    
    Args:
        num_keys: Количество ключей для анализа
    """
    ht = HashTable(size=2500)
    hash_distribution = Counter()
    
    print(f"Генерация {num_keys} ключей...")
    keys_generated = []
    for i in range(num_keys):
        key = generate_key()
        keys_generated.append(key)
        h1 = ht.hash1(key)
        hash_distribution[h1] += 1
        
        if (i + 1) % 1000 == 0:
            print(f"Обработано {i + 1} ключей...")
    
    # Статистика
    print(f"\n=== Результаты анализа хеш-функции ===")
    print(f"Количество сегментов: {ht.size}")
    print(f"Количество ключей: {num_keys}")
    print(f"Заполненных сегментов: {len(hash_distribution)}")
    print(f"Пустых сегментов: {ht.size - len(hash_distribution)}")
    
    # Статистика по коллизиям
    collision_counts = list(hash_distribution.values())
    if collision_counts:
        print(f"\nСтатистика коллизий:")
        print(f"  Минимальное количество попаданий в сегмент: {min(collision_counts)}")
        print(f"  Максимальное количество попаданий в сегмент: {max(collision_counts)}")
        print(f"  Среднее количество попаданий: {sum(collision_counts) / len(collision_counts):.2f}")
        print(f"  Ожидаемое среднее: {num_keys / ht.size:.2f}")
        
        # Подсчет сегментов с разным количеством попаданий
        collision_dist = Counter(collision_counts)
        print(f"\nРаспределение сегментов по количеству попаданий:")
        for count in sorted(collision_dist.keys()):
            segments = collision_dist[count]
            percentage = (segments / ht.size) * 100
            print(f"  {count} попаданий: {segments} сегментов ({percentage:.2f}%)")
    
    # Сохранение результатов для построения гистограммы
    output_file = "hash_analysis.csv"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Сегмент,Количество_попаданий\n")
        for segment in range(ht.size):
            count = hash_distribution.get(segment, 0)
            f.write(f"{segment},{count}\n")
    
    print(f"\nРезультаты сохранены в файл: {output_file}")
    print("Файл можно использовать для построения гистограммы в MS Excel")
    
    return hash_distribution


if __name__ == '__main__':
    analyze_hash_distribution(7500)

