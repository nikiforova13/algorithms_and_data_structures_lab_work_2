import re
from typing import Optional, Tuple, List


class HashTable:
    """
    Хеш-таблица с открытым хешированием (метод цепочек) для разрешения коллизий.
    Формат ключа: цББББц (1 цифра, 4 большие буквы, 1 цифра)
    Количество сегментов: 1500
    """
    
    # Формат ключа: 1 цифра, 4 большие буквы, 1 цифра
    KEY_PATTERN = re.compile(r'^\d[A-Z]{4}\d$')
    
    def __init__(self, size: int = 1500):
        """
        Инициализация хеш-таблицы.
        
        Args:
            size: Размер таблицы (количество сегментов)
        """
        self.size = size
        # Каждый сегмент - это список элементов (цепочка)
        self.table: List[List[Tuple[str, any]]] = [[] for _ in range(size)]
        self.count = 0  # Количество элементов в таблице
    
    def validate_key(self, key: str) -> bool:
        """
        Проверяет формат ключа.
        
        Args:
            key: Ключ для проверки
            
        Returns:
            True если ключ соответствует формату цББББц, иначе False
        """
        return bool(self.KEY_PATTERN.match(key))
    
    def hash(self, key: str) -> int:
        """
        Хеш-функция.
        Использует полиномиальное хеширование.
        
        Args:
            key: Ключ для хеширования
            
        Returns:
            Хеш-значение (номер сегмента)
        """
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 31 + ord(char)) % self.size
        return hash_value
    
    def add(self, key: str, value: any = None) -> bool:
        """
        Добавляет элемент в хеш-таблицу.
        
        Args:
            key: Ключ элемента (формат цББББц)
            value: Значение элемента
            
        Returns:
            True если элемент добавлен, False если неверный ключ или переполнение
        """
        if not self.validate_key(key):
            return False
        
        # Проверка переполнения
        filled_segments = sum(1 for chain in self.table if chain)
        if filled_segments > 0:
            avg_chain_length = self.count / filled_segments
        else:
            avg_chain_length = 0
        
        # Критическое переполнение: средняя длина цепочки > 20 или все сегменты заполнены и средняя длина > 15
        if avg_chain_length > 20:
            print("⚠ ОШИБКА: Критическое переполнение! Средняя длина цепочки превышает 20 элементов!")
            return False
        
        if filled_segments == self.size and avg_chain_length > 15:
            print("⚠ ОШИБКА: Критическое переполнение! Все сегменты заполнены и средняя длина цепочки > 15!")
            return False
        
        # Предупреждения
        if avg_chain_length > 10:
            print("⚠ ПРЕДУПРЕЖДЕНИЕ: Средняя длина цепочки превышает 10 элементов!")
        
        if self.count >= self.size * 0.95:
            print("⚠ ПРЕДУПРЕЖДЕНИЕ: Таблица заполнена более чем на 95%!")
        
        # Вычисляем сегмент
        segment = self.hash(key)
        chain = self.table[segment]
        
        # Проверяем, существует ли уже элемент с таким ключом
        for i, (k, v) in enumerate(chain):
            if k == key:
                # Обновляем существующий элемент
                chain[i] = (key, value)
                return True
        
        # Добавляем новый элемент в цепочку
        chain.append((key, value))
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
        if not self.validate_key(key):
            return None
        
        segment = self.hash(key)
        chain = self.table[segment]
        
        for k, v in chain:
            if k == key:
                return v
        
        return None
    
    def search_by_key(self, key: str) -> Optional[Tuple[int, str, any]]:
        """
        Ищет элемент по ключу.
        
        Args:
            key: Ключ для поиска
            
        Returns:
            Кортеж (номер сегмента, ключ, значение) или None если не найдено
        """
        if not self.validate_key(key):
            return None
        
        segment = self.hash(key)
        chain = self.table[segment]
        
        for k, v in chain:
            if k == key:
                return (segment, k, v)
        
        return None
    
    def search_by_segment(self, segment: int) -> Optional[List[Tuple[str, any]]]:
        """
        Ищет элементы по номеру сегмента.
        
        Args:
            segment: Номер сегмента (индекс)
            
        Returns:
            Список кортежей (ключ, значение) или None если сегмент не существует
        """
        if segment < 0 or segment >= self.size:
            return None
        
        chain = self.table[segment]
        if not chain:
            return None
        
        return chain.copy()
    
    def delete(self, key: str) -> Tuple[bool, List[str]]:
        """
        Удаляет элемент из хеш-таблицы.
        Также находит все элементы, которые имели коллизию с удаляемым.
        
        Args:
            key: Ключ для удаления
            
        Returns:
            Кортеж (успех удаления, список ключей элементов с коллизией)
        """
        if not self.validate_key(key):
            return (False, [])
        
        segment = self.hash(key)
        chain = self.table[segment]
        
        # Ищем элемент для удаления
        found = False
        for i, (k, v) in enumerate(chain):
            if k == key:
                # Удаляем элемент
                chain.pop(i)
                self.count -= 1
                found = True
                break
        
        if not found:
            return (False, [])
        
        # Ищем элементы с коллизией (все остальные элементы в том же сегменте)
        collision_keys = [k for k, v in chain if k != key]
        
        return (True, collision_keys)
    
    def view(self) -> List[Tuple[int, Optional[str], Optional[any]]]:
        """
        Просматривает содержимое хеш-таблицы.
        
        Returns:
            Список кортежей (номер сегмента, ключ, значение)
            Для каждого элемента в цепочке создается отдельная запись
        """
        result = []
        for i in range(self.size):
            chain = self.table[i]
            if not chain:
                # Пустой сегмент
                result.append((i, None, None))
            else:
                # Для каждого элемента в цепочке
                for key, value in chain:
                    result.append((i, key, value))
        
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
                f.write('Сегмент,Ключ,Значение,Длина_цепочки\n')
                for i in range(self.size):
                    chain = self.table[i]
                    chain_length = len(chain)
                    if not chain:
                        f.write(f'{i},,,0\n')
                    else:
                        for key, value in chain:
                            f.write(f'{i},{key},{value},{chain_length}\n')
            
            # Создаем файл для гистограммы (распределение по сегментам)
            hist_filename = filename.replace('.csv', '_histogram.csv')
            with open(hist_filename, 'w', encoding='utf-8') as f:
                f.write('Сегмент,Количество_элементов,Длина_цепочки\n')
                for i in range(self.size):
                    chain_length = len(self.table[i])
                    f.write(f'{i},{chain_length},{chain_length}\n')
            
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
        filled_segments = sum(1 for chain in self.table if chain)
        empty_segments = sum(1 for chain in self.table if not chain)
        
        # Статистика по длинам цепочек
        chain_lengths = [len(chain) for chain in self.table if chain]
        max_chain_length = max(chain_lengths) if chain_lengths else 0
        avg_chain_length = sum(chain_lengths) / len(chain_lengths) if chain_lengths else 0
        
        return {
            'size': self.size,
            'filled': filled_segments,
            'empty': empty_segments,
            'count': self.count,
            'fill_percentage': (filled_segments / self.size * 100) if self.size > 0 else 0,
            'max_chain_length': max_chain_length,
            'avg_chain_length': round(avg_chain_length, 2)
        }
