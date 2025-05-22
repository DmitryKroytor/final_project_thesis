import os
import matplotlib.pyplot as plt
import pandas as pd

INPUT_MAP_PATH = '../parser/parsed_data/maps'
INPUT_VAC_PATH = '../parser/parsed_data/vac'

OUTPUT_MAPS_PATH = '../../data/images/maps'
OUTPUT_VACS_PATH = '../../data/images/vacs'
OUTPUT_J_c_PATH = '../../data/images/J_c'


def draw_maps(input_path, output_path):
    names = [name for name in os.listdir(input_path)]

    for name in names:
        df = pd.read_csv(f'{input_path}/{name}')

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        surf = ax.plot_trisurf(df['x'], df['y'], df['B'], cmap='viridis', edgecolor='none')

        cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
        cbar.set_label('B (mT)', fontsize=12)

        ax.set_xlabel("x (mm)")
        ax.set_ylabel("y (mm)")
        ax.set_zlabel("B (mT)")
        path = f'{output_path}/{name[:-4]}.png'
        plt.savefig(path)
        plt.close()

        print(f"Сохранён график: {path}")


def draw_vacs(input_path, output_path):
    names = [name for name in os.listdir(input_path)]

    for name in names:
        df = pd.read_csv(f'{input_path}/{name}')
        plt.figure(figsize=(8, 6))
        plt.plot(df['I'], df['U'], label="VAC", linewidth=2)
        plt.xlabel("I (A)")
        plt.ylabel("U (V)")
        plt.title("VAC")
        plt.grid(True)
        plt.legend()
        path = f'{output_path}/{name[:-4]}.png'
        plt.savefig(path)
        plt.close()

        print(f"Сохранён график: {path}")


def draw_Jc(df):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    df['x'] = df['x'] * 1e3
    df['y'] = df['y'] * 1e3
    surf = ax.plot_trisurf(df['x'], df['y'], df['Jc'], cmap='viridis', edgecolor='none')

    cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label('J_c (A/m^2)', fontsize=12)
    title = df['title'].iloc[0]
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("J_c (A/m^2)")
    path = f'{OUTPUT_J_c_PATH}/{title}.png'
    plt.savefig(path)
    plt.close()

    print(f"Сохранён график: {path}")


# draw_maps(INPUT_MAP_PATH, OUTPUT_MAPS_PATH)
# draw_vacs(INPUT_VAC_PATH, OUTPUT_VACS_PATH)
