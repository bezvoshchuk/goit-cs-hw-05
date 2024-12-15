import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, Counter

import matplotlib.pyplot as plt
import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевіряємо на HTTP помилки
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word.lower(), 1  # Повертаємо слово в нижньому регістрі і кількість (1)


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    if search_words:
        words = [word for word in words if word.lower() in search_words]

    # 1: Паралельний маппінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # 3: Паралельна редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


# Візуалізація
def visualize_top_words(result, top_n=10):
    top_words = Counter(result).most_common(top_n)

    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color="skyblue")
    plt.xlabel("Frequency")
    plt.ylabel("Words")
    plt.title(f"Top {top_n} Most Frequent Words")
    plt.gca().invert_yaxis()  # Перевернути графік, щоб найбільші значення були зверху
    plt.show()


if __name__ == "__main__":
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"  # Текст для обробки
    text = get_text(url)

    if text:
        result = map_reduce(text)
        visualize_top_words(result)
    else:
        print("Failed to retrieve text.")
