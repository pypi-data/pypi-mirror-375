def load_1_1():
    print("""import os
import struct


def get_file_type(file_path):
    \"\"\"Определяет тип файла по сигнатуре\"\"\"
    signatures = {
        b"\\xff\\xd8\\xff": "JPEG",
        b"\\x89PNG\\r\\n\\x1a\\n": "PNG",
        b"BM": "BMP",
        b"GIF87a": "GIF87a",
        b"GIF89a": "GIF89a",
        b"II*\\x00": "TIFF",
        b"MM\\x00*": "TIFF",
        b"RIFF": "WEBP",
    }

    try:
        with open(file_path, "rb") as f:
            header = f.read(12)

        for sig, ftype in signatures.items():
            if header.startswith(sig):
                return ftype
        return "Unknown"
    except:
        return "Error\"""")

def load_1_2():
    print("""
def main():
    # Запрашиваем путь к папке у пользователя
    folder_path = input("Введите путь до анализируемой папки: ").strip()

    # Удаляем кавычки, если пользователь ввел путь в кавычках
    folder_path = folder_path.strip("\\"'")

    # Проверяем, существует ли указанная папка
    if not os.path.exists(folder_path):
        print(f"Ошибка: Папка '{folder_path}' не существует!")
        return

    if not os.path.isdir(folder_path):
        print(f"Ошибка: '{folder_path}' не является папкой!")
        return

    # Поддерживаемые расширения
    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}

    # Счетчик файлов
    file_count = 0

    print(f"\\nАнализ папки: {folder_path}")
    print("-" * 50)

    # Рекурсивный обход всех папок и подпапок
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if os.path.splitext(filename)[1].lower() in extensions:
                file_path = os.path.join(root, filename)
                file_type = get_file_type(file_path)
                print(f"Файл: {filename}, Тип файла: {file_type}")
                file_count += 1

    # Вывод общего количества файлов
    print("-" * 50)
    print(f"\\nОбщее количество проанализированных файлов: {file_count}")


if __name__ == "__main__":
    main()""")

def load_3_1():
    print("""# Импорт необходимых библиотек
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt
import os

# Указание пути до папки с датасетом
data_dir = r"C:\\.....uuuuuu"

# Параметры изображений и batch size
img_height = 180
img_width = 180
batch_size = 32

# Создание набора данных для обучения
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
)

# Создание набора данных для валидации
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(img_height, img_width),
    batch_size=batch_size,
)

# Извлечение имен классов
class_names = train_ds.class_names
print("Классы в датасете:", class_names)

# Кэширование данных для оптимальной производительности
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# Определение количества классов
num_classes = len(class_names)""")

def load_3_2():
    print("""# Создание модели нейронной сети
model = keras.Sequential(
    [
        # Масштабирование значений пикселей к диапазону [0, 1]
        layers.Rescaling(1.0 / 255, input_shape=(img_height, img_width, 3)),
        # Аугментация данных
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.2),
        # Первая пара сверточный + пулинговый слои
        layers.Conv2D(16, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        # Вторая пара сверточный + пулинговый слои
        layers.Conv2D(32, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        # Третья пара сверточный + пулинговый слои
        layers.Conv2D(64, 3, padding="same", activation="relu"),
        layers.MaxPooling2D(),
        # Регуляризация и преобразование в 1D
        layers.Dropout(0.2),
        layers.Flatten(),
        # Полносвязный слой
        layers.Dense(128, activation="relu"),
        # Выходной слой
        layers.Dense(num_classes),
    ]
)

# Компиляция модели
model.compile(
    optimizer="adam",
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

# Обучение модели
epochs = 10
history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)

# Извлечение данных для визуализации
acc = history.history["accuracy"]
val_acc = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]

# Создание диапазона эпох
epochs_range = range(epochs)

# Создание графиков
plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label="Точность обучения")
plt.plot(epochs_range, val_acc, label="Точность валидации")
plt.legend(loc="lower right")
plt.title("Точность тренировки и валидации")

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label="Ошибка обучения")
plt.plot(epochs_range, val_loss, label="Ошибка валидации")
plt.legend(loc="upper right")
plt.title("Ошибка тренировки и валидации")

plt.show()

# Сохранение модели
model.save("modul_B_3.h5")
print("Модель успешно сохранена в формате HDF5 как 'modul_B_3.h5'")""")

def load_4_1():
    print("""import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

test_dir = r"C:\\.....uuu"
img_height, img_width = 180, 180
model = load_model("modul_B_3.h5")
class_names = [
    "chicken",
    "cows",
    "geese",
    "goats",
    "horses",
    "pigs",
    "rabbits",
    "sheep",
]
class_counts = {class_name: 0 for class_name in class_names}""")

def load_4_2():
    print("""
for root, _, files in os.walk(test_dir):
    for img_name in files:
        img_path = os.path.join(root, img_name)
        img = image.load_img(img_path, target_size=(img_height, img_width))
        img_array = np.expand_dims(image.img_to_array(img), axis=0)

        predictions = model.predict(img_array, verbose=0)
        score = tf.nn.softmax(predictions[0])

        class_index = np.argmax(score)
        class_name = class_names[class_index]
        confidence = 100 * np.max(score)

        class_counts[class_name] += 1
        print(
            f"Изображение '{os.path.relpath(img_path, test_dir)}' - класс '{class_name}' ({confidence:.2f}%)"
        )

print("\\nИтоговая статистика:")
for class_name, count in class_counts.items():
    print(f"Класс '{class_name}': {count} изображений")""")

def load_5_1():
    print("""import os
import shutil
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Пути
source_path = r"C:\\....uuuu"
target_path = r"Proverka_5_test"

# Классы и загрузка модели
classes = ["chicken", "cows", "geese", "goats", "horses", "pigs", "rabbits", "sheep"]
model = load_model("modul_B_3.h5")

# Фиксированный размер изображения
target_size = (180, 180)

# Создание подпапок
for class_name in classes:
    os.makedirs(os.path.join(target_path, class_name), exist_ok=True)""")

def load_5_2():
    print("""
# Обработка изображений
for filename in os.listdir(source_path):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        img_path = os.path.join(source_path, filename)

        try:
            # Загрузка и предобработка изображения с размером 180x180
            img = image.load_img(img_path, target_size=target_size)
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)

            # Предсказание
            prediction = model.predict(img_array, verbose=0)
            class_idx = np.argmax(prediction)
            predicted_class = classes[class_idx]

            # Перемещение файла
            dest_path = os.path.join(target_path, predicted_class, filename)
            shutil.move(img_path, dest_path)

            # Вывод информации
            print(f"{filename} – перемещен в: {predicted_class}")

        except Exception as e:
            print(f"Ошибка при обработке {filename}: {e}")

print("\\nОбработка завершена!")""")