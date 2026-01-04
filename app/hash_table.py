import re
from typing import Optional, Tuple, List


class HashTable:
    """
    Хеш-таблица с двойным хешированием для разрешения коллизий.
    Формат ключа: цццБцц (3 цифры, 1 большая буква, 2 цифры)
    Количество сегментов: 2500
    """
    
    # Формат ключа: 3 цифры, 1 большая буква, 2 цифры
    KEY_PATTERN = re.compile(r'^\d{3}[A-Z]\d{2}$')
    
    def __init__(self, size: int = 2500):
        """
        Инициализация хеш-таблицы.
        
        Args:
            size: Размер таблицы (количество сегментов)
        """
        self.size = size
        self.table: List[Optional[Tuple[str, any]]] = [None] * size
        self.count = 0  # Количество элементов в таблице
        self.deleted_marker = object()  # Маркер удаленного элемента
    
    def validate_key(self, key: str) -> bool:
        """
        Проверяет формат ключа.
        
        Args:
            key: Ключ для проверки
            
        Returns:
            True если ключ соответствует формату цццБцц, иначе False
        """
        return bool(self.KEY_PATTERN.match(key))
    
    def hash1(self, key: str) -> int:
        """
        Первая хеш-функция (основная).
        Использует полиномиальное хеширование.
        
        Args:
            key: Ключ для хеширования
            
        Returns:
            Хеш-значение
        """
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 31 + ord(char)) % self.size
        return hash_value
    
    def hash2(self, key: str) -> int:
        """
        Вторая хеш-функция для двойного хеширования.
        Должна возвращать значение, взаимно простое с размером таблицы.
        
        Args:
            key: Ключ для хеширования
            
        Returns:
            Хеш-значение для шага
        """
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 37 + ord(char)) % self.size
        
        # Убеждаемся, что hash2 не равен 0 и взаимно прост с size
        if hash_value == 0:
            hash_value = 1
        
        # Если size четное, делаем hash2 нечетным
        if self.size % 2 == 0 and hash_value % 2 == 0:
            hash_value += 1
        
        return hash_value
    
    def find_position(self, key: str, for_insert: bool = False) -> Optional[int]:
        """
        Находит позицию для ключа в таблице.
        
        Args:
            key: Ключ для поиска
            for_insert: Если True, ищет позицию для вставки (может вернуть позицию удаленного элемента)
            
        Returns:
            Индекс позиции или None если не найдено (и for_insert=False)
        """
        if not self.validate_key(key):
            return None
        
        h1 = self.hash1(key)
        h2 = self.hash2(key)
        
        for i in range(self.size):
            index = (h1 + i * h2) % self.size
            item = self.table[index]
            
            if item is None:
                # Пустая ячейка найдена
                if for_insert:
                    return index
                else:
                    return None
            
            if item is self.deleted_marker:
                # Удаленная ячейка - продолжаем поиск для вставки
                if for_insert:
                    continue
            
            if isinstance(item, tuple) and item[0] == key:
                return index
        
        return None
    
    def add(self, key: str, value: any = None) -> bool:
        """
        Добавляет элемент в хеш-таблицу.
        
        Args:
            key: Ключ элемента (формат цццБцц)
            value: Значение элемента
            
        Returns:
            True если элемент добавлен, False если таблица переполнена или неверный ключ
        """
        if not self.validate_key(key):
            return False
        
        # Проверка переполнения
        if self.count >= self.size * 0.9:  # Предупреждение при заполнении >90%
            if self.count >= self.size:
                return False  # Таблица переполнена
        
        # Проверяем, существует ли уже элемент с таким ключом
        existing_pos = self.find_position(key, for_insert=False)
        if existing_pos is not None:
            # Обновляем существующий элемент
            self.table[existing_pos] = (key, value)
            return True
        
        # Ищем позицию для вставки
        pos = self.find_position(key, for_insert=True)
        if pos is None:
            return False  # Не найдено место (переполнение)
        
        self.table[pos] = (key, value)
        self.count += 1
        return True
    
    def get(self, key: str) -> Optional[any]:
        """
        Получает значение по ключу.
        
        Args:
            key: Ключ для поиска
            
        Returns:
            Значение элемента или None если не найдено
        """
        pos = self.find_position(key, for_insert=False)
        if pos is not None:
            return self.table[pos][1]
        return None
    
    def search_by_key(self, key: str) -> Optional[Tuple[int, str, any]]:
        """
        Ищет элемент по ключу.
        
        Args:
            key: Ключ для поиска
            
        Returns:
            Кортеж (номер сегмента, ключ, значение) или None если не найдено
        """
        pos = self.find_position(key, for_insert=False)
        if pos is not None:
            item = self.table[pos]
            if isinstance(item, tuple):
                return (pos, item[0], item[1])
        return None
    
    def search_by_segment(self, segment: int) -> Optional[Tuple[str, any]]:
        """
        Ищет элемент по номеру сегмента.
        
        Args:
            segment: Номер сегмента (индекс)
            
        Returns:
            Кортеж (ключ, значение) или None если сегмент пуст или удален
        """
        if segment < 0 or segment >= self.size:
            return None
        
        item = self.table[segment]
        if item is None or item is self.deleted_marker:
            return None
        
        if isinstance(item, tuple):
            return item
        
        return None
    
    def delete(self, key: str) -> Tuple[bool, List[str]]:
        """
        Удаляет элемент из хеш-таблицы.
        Также находит все элементы, которые имели коллизию с удаляемым.
        
        Args:
            key: Ключ для удаления
            
        Returns:
            Кортеж (успех удаления, список ключей элементов с коллизией)
        """
        pos = self.find_position(key, for_insert=False)
        if pos is None:
            return (False, [])
        
        # Сохраняем информацию об удаляемом элементе
        deleted_item = self.table[pos]
        deleted_key = deleted_item[0] if isinstance(deleted_item, tuple) else key
        
        # Помечаем ячейку как удаленную
        self.table[pos] = self.deleted_marker
        self.count -= 1
        
        # Ищем элементы с коллизией
        collision_keys = self._find_collision_elements(deleted_key, pos)
        
        return (True, collision_keys)
    
    def _find_collision_elements(self, deleted_key: str, deleted_pos: int) -> List[str]:
        """
        Находит элементы, которые имели коллизию с удаленным элементом.
        
        В двойном хешировании коллизия возникает, когда два ключа имеют одинаковую
        начальную позицию (h1(key1) == h1(key2)). Также проверяем элементы, которые
        находятся на позициях, через которые проходил удаленный элемент при вставке.
        
        Args:
            deleted_key: Ключ удаленного элемента
            deleted_pos: Позиция удаленного элемента
            
        Returns:
            Список ключей элементов с коллизией
        """
        collision_keys = []
        h1_deleted = self.hash1(deleted_key)
        h2_deleted = self.hash2(deleted_key)
        
        # Вычисляем последовательность позиций, через которые проходил удаленный элемент
        deleted_path = set()
        for i in range(self.size):
            pos = (h1_deleted + i * h2_deleted) % self.size
            deleted_path.add(pos)
            if pos == deleted_pos:
                break
        
        # Проверяем все элементы в таблице
        for i in range(self.size):
            item = self.table[i]
            if item is None or item is self.deleted_marker:
                continue
            
            if isinstance(item, tuple):
                item_key = item[0]
                if item_key == deleted_key:
                    continue  # Пропускаем сам удаленный элемент
                
                item_h1 = self.hash1(item_key)
                
                # Коллизия: если начальные позиции совпадают
                if item_h1 == h1_deleted:
                    collision_keys.append(item_key)
                # Также проверяем, находится ли элемент на пути удаленного
                elif i in deleted_path:
                    # Проверяем, действительно ли этот элемент должен был быть в этой позиции
                    # или попал туда из-за коллизии
                    item_h2 = self.hash2(item_key)
                    item_expected_pos = item_h1  # Начальная позиция элемента
                    if item_expected_pos in deleted_path:
                        collision_keys.append(item_key)
        
        return list(set(collision_keys))  # Убираем дубликаты
    
    def view(self) -> List[Tuple[int, Optional[str], Optional[any]]]:
        """
        Просматривает содержимое хеш-таблицы.
        
        Returns:
            Список кортежей (номер сегмента, ключ, значение)
        """
        result = []
        for i in range(self.size):
            item = self.table[i]
            if item is None:
                result.append((i, None, None))
            elif item is self.deleted_marker:
                result.append((i, None, None))  # Удаленные элементы показываем как пустые
            elif isinstance(item, tuple):
                result.append((i, item[0], item[1]))
        return result
    
    def export_to_csv(self, filename: str = 'hash_table_export.csv') -> bool:
        """
        Выгружает содержимое хеш-таблицы в CSV файл для построения гистограммы.
        
        Args:
            filename: Имя файла для экспорта
            
        Returns:
            True если экспорт успешен
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('Сегмент,Ключ,Значение,Заполненность\n')
                for i in range(self.size):
                    item = self.table[i]
                    if item is None or item is self.deleted_marker:
                        f.write(f'{i},,,\n')
                    elif isinstance(item, tuple):
                        f.write(f'{i},{item[0]},{item[1]},1\n')
            
            # Создаем файл для гистограммы (распределение по сегментам)
            hist_filename = filename.replace('.csv', '_histogram.csv')
            with open(hist_filename, 'w', encoding='utf-8') as f:
                f.write('Сегмент,Количество элементов\n')
                filled_count = 0
                for i in range(self.size):
                    item = self.table[i]
                    if item is not None and item is not self.deleted_marker:
                        filled_count += 1
                f.write(f'Заполненные,{filled_count}\n')
                f.write(f'Пустые,{self.size - filled_count}\n')
            
            return True
        except Exception as e:
            print(f"Ошибка при экспорте: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """
        Возвращает статистику по хеш-таблице.
        
        Returns:
            Словарь со статистикой
        """
        filled = sum(1 for item in self.table 
                    if item is not None and item is not self.deleted_marker)
        empty = sum(1 for item in self.table if item is None)
        deleted = sum(1 for item in self.table if item is self.deleted_marker)
        
        return {
            'size': self.size,
            'filled': filled,
            'empty': empty,
            'deleted': deleted,
            'count': self.count,
            'fill_percentage': (filled / self.size * 100) if self.size > 0 else 0
        }

