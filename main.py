"""
Лабораторная работа №2
Хеширование данных. Хеш-таблица с открытым хешированием.

Вариант 21:
- Формат ключа: цББББц (1 цифра, 4 большие буквы, 1 цифра)
- Количество сегментов: 1500
- Метод разрешения коллизий: Открытое хеширование (метод цепочек)
"""

from app.hash_table import HashTable


def print_menu():
    """Выводит меню программы."""
    print("\n" + "="*60)
    print("ХЕШ-ТАБЛИЦА С ОТКРЫТЫМ ХЕШИРОВАНИЕМ")
    print("="*60)
    print("1. Добавить элемент")
    print("2. Найти элемент по ключу")
    print("3. Найти элемент по номеру сегмента")
    print("4. Просмотреть хеш-таблицу")
    print("5. Удалить элемент")
    print("6. Выгрузить данные в файл (CSV)")
    print("7. Показать статистику")
    print("8. Очистить таблицу")
    print("0. Выход")
    print("="*60)


def add_element(ht: HashTable):
    """Добавляет элемент в хеш-таблицу."""
    print("\n--- Добавление элемента ---")
    key = input("Введите ключ (формат: цББББц, например: 1ABCD2): ").strip()
    
    if not ht.validate_key(key):
        print("ОШИБКА: Неверный формат ключа!")
        print("Формат должен быть: цББББц (1 цифра, 4 большие буквы, 1 цифра)")
        print("Примеры: 1ABCD2, 9XYZQ0, 5QWER3")
        return
    
    value = input("Введите значение (или Enter для ключа): ").strip()
    if not value:
        value = key
    
    if ht.add(key, value):
        segment = ht.hash(key)
        print(f"✓ Элемент успешно добавлен в сегмент {segment}")
    else:
        stats = ht.get_statistics()
        if stats['avg_chain_length'] > 10:
            print("ОШИБКА: Хеш-таблица переполнена (средняя длина цепочки > 10)!")
        else:
            print("ОШИБКА: Не удалось добавить элемент")


def search_by_key(ht: HashTable):
    """Ищет элемент по ключу."""
    print("\n--- Поиск по ключу ---")
    key = input("Введите ключ для поиска: ").strip()
    
    if not ht.validate_key(key):
        print("ОШИБКА: Неверный формат ключа!")
        return
    
    result = ht.search_by_key(key)
    if result:
        segment, found_key, value = result
        print(f"✓ Элемент найден:")
        print(f"  Сегмент: {segment}")
        print(f"  Ключ: {found_key}")
        print(f"  Значение: {value}")
    else:
        print("✗ Элемент с таким ключом не найден")


def search_by_segment(ht: HashTable):
    """Ищет элементы по номеру сегмента."""
    print("\n--- Поиск по номеру сегмента ---")
    try:
        segment = int(input(f"Введите номер сегмента (0-{ht.size-1}): ").strip())
        result = ht.search_by_segment(segment)
        if result:
            print(f"✓ Найдено {len(result)} элементов в сегменте {segment}:")
            print("-" * 60)
            print(f"{'Ключ':<15} {'Значение':<20}")
            print("-" * 60)
            for key, value in result:
                print(f"{key:<15} {str(value):<20}")
        else:
            print(f"✗ Сегмент {segment} пуст")
    except ValueError:
        print("ОШИБКА: Введите корректное число")


def view_table(ht: HashTable):
    """Просматривает хеш-таблицу."""
    print("\n--- Просмотр хеш-таблицы ---")
    
    view_mode = input("Показать только заполненные сегменты? (y/n): ").strip().lower()
    show_only_filled = view_mode == 'y'
    
    data = ht.view()
    filled_count = 0
    
    if show_only_filled:
        filled_items = [(seg, key, val) for seg, key, val in data if key is not None]
        if filled_items:
            print(f"\nЭлементы в заполненных сегментах ({len(filled_items)} элементов):")
            print("-" * 60)
            print(f"{'Сегмент':<10} {'Ключ':<15} {'Значение':<20}")
            print("-" * 60)
            for seg, key, val in filled_items:
                print(f"{seg:<10} {key:<15} {str(val):<20}")
                filled_count += 1
        else:
            print("Таблица пуста")
    else:
        print(f"\nВсе элементы (первые 50):")
        print("-" * 60)
        print(f"{'Сегмент':<10} {'Ключ':<15} {'Значение':<20}")
        print("-" * 60)
        for seg, key, val in data[:50]:
            if key is not None:
                print(f"{seg:<10} {key:<15} {str(val):<20}")
                filled_count += 1
            else:
                if not show_only_filled:
                    print(f"{seg:<10} {'---':<15} {'---':<20}")
        
        if len(data) > 50:
            print(f"... и еще {len(data) - 50} элементов")
    
    print("-" * 60)


def delete_element(ht: HashTable):
    """Удаляет элемент из хеш-таблицы."""
    print("\n--- Удаление элемента ---")
    key = input("Введите ключ для удаления: ").strip()
    
    if not ht.validate_key(key):
        print("ОШИБКА: Неверный формат ключа!")
        return
    
    success, collision_keys = ht.delete(key)
    if success:
        print(f"✓ Элемент с ключом '{key}' успешно удален")
        if collision_keys:
            print(f"\nЭлементы, которые имели коллизию с удаленным:")
            for coll_key in collision_keys:
                print(f"  - {coll_key}")
        else:
            print("Элементы с коллизией не обнаружены")
    else:
        print("✗ Элемент с таким ключом не найден")


def export_data(ht: HashTable):
    """Выгружает данные в CSV файл."""
    print("\n--- Экспорт данных ---")
    filename = input("Введите имя файла (или Enter для hash_table_export.csv): ").strip()
    if not filename:
        filename = "hash_table_export.csv"
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    if ht.export_to_csv(filename):
        print(f"✓ Данные успешно выгружены в файл '{filename}'")
        print(f"  Файл гистограммы: {filename.replace('.csv', '_histogram.csv')}")
    else:
        print("✗ Ошибка при выгрузке данных")


def show_statistics(ht: HashTable):
    """Показывает статистику по хеш-таблице."""
    print("\n--- Статистика хеш-таблицы ---")
    stats = ht.get_statistics()
    print(f"Размер таблицы: {stats['size']}")
    print(f"Заполненных сегментов: {stats['filled']}")
    print(f"Пустых сегментов: {stats['empty']}")
    print(f"Количество элементов: {stats['count']}")
    print(f"Процент заполнения сегментов: {stats['fill_percentage']:.2f}%")
    print(f"Максимальная длина цепочки: {stats['max_chain_length']}")
    print(f"Средняя длина цепочки: {stats['avg_chain_length']}")
    
    if stats['fill_percentage'] >= 90:
        print("\n⚠ ВНИМАНИЕ: Более 90% сегментов заполнены!")
    if stats['avg_chain_length'] > 10:
        print("\n⚠ ВНИМАНИЕ: Средняя длина цепочки превышает 10 элементов!")
    if stats['max_chain_length'] > 20:
        print("\n⚠ ВНИМАНИЕ: Обнаружены очень длинные цепочки!")


def clear_table(ht: HashTable):
    """Очищает хеш-таблицу."""
    print("\n--- Очистка таблицы ---")
    confirm = input("Вы уверены? Все данные будут удалены (y/n): ").strip().lower()
    if confirm == 'y':
        ht.table = [[] for _ in range(ht.size)]
        ht.count = 0
        print("✓ Таблица очищена")
    else:
        print("Отменено")


def main():
    """Главная функция программы."""
    print("Инициализация хеш-таблицы...")
    ht = HashTable(size=1500)
    print(f"✓ Хеш-таблица создана (размер: {ht.size} сегментов)")
    print("Формат ключа: цББББц (1 цифра, 4 большие буквы, 1 цифра)")
    print("Примеры: 1ABCD2, 9XYZQ0, 5QWER3")
    
    while True:
        print_menu()
        choice = input("\nВыберите действие: ").strip()
        
        if choice == '1':
            add_element(ht)
        elif choice == '2':
            search_by_key(ht)
        elif choice == '3':
            search_by_segment(ht)
        elif choice == '4':
            view_table(ht)
        elif choice == '5':
            delete_element(ht)
        elif choice == '6':
            export_data(ht)
        elif choice == '7':
            show_statistics(ht)
        elif choice == '8':
            clear_table(ht)
        elif choice == '0':
            print("\nДо свидания!")
            break
        else:
            print("Неверный выбор! Попробуйте снова.")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == '__main__':
    main()
