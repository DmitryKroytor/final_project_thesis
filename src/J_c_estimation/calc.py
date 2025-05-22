import pandas as pd
import numpy as np
# from src.graphs.drawer import draw_Jc
import os

from src.graphs.drawer import draw_Jc


def calculate_Jc(input_path, output_path):
    names = [name for name in os.listdir(input_path)]

    mu0 = 4 * np.pi * 1e-7  # Магнитная проницаемость
    d = 4e-6  # Толщина образца, м
    h = 1e-3  # Высота измерения над образцом, м

    result_df = pd.DataFrame(columns=["title", "x", "y", "B"])
    result_df = result_df.astype({"title": "str", "x": "float64", "y": "float64", "B": "float64"})

    for name in names:
        df = pd.read_csv(f'{input_path}/{name}')

        x = df['x'].values * 1e-3  # Конвертация мм в метры
        y = df['y'].values * 1e-3
        Bz = df['B'].values * 1e-3  # Конвертация мТл в Тл

        x_unique = np.unique(x)
        y_unique = np.unique(y)
        Nx = len(x_unique)
        Ny = len(y_unique)
        Bz_matrix = Bz.reshape(Ny, Nx)

        dx = (x_unique.max() - x_unique.min()) / (Nx - 1)  # Шаг по x (метры)
        dy = (y_unique.max() - y_unique.min()) / (Ny - 1)  # Шаг по y (метры)
        X, Y = np.meshgrid(x_unique, y_unique)

        Bz_fft = np.fft.fft2(Bz_matrix)

        kx = 2 * np.pi * np.fft.fftfreq(Nx, d=dx)
        ky = 2 * np.pi * np.fft.fftfreq(Ny, d=dy)
        Kx, Ky = np.meshgrid(kx, ky)
        k = np.sqrt(Kx ** 2 + Ky ** 2)

        g_fft = np.zeros_like(Bz_fft, dtype=complex)
        mask = k != 0  # Избегаем деления на ноль
        g_fft[mask] = 2 * Bz_fft[mask] * np.exp(h * k[mask]) / (mu0 * k[mask] * d)
        g_fft[~mask] = 0
        g = np.fft.ifft2(g_fft).real

        gy, gx = np.gradient(g, dy, dx)
        jx = gy
        jy = -gx
        j = np.sqrt(jx ** 2 + jy ** 2)

        # Вычисление градиентов
        df['x_m'] = df['x'] * 1e-3
        df['y_m'] = df['y'] * 1e-3
        df['B_T'] = df['B'] * 1e-3

        pivot = df.pivot(index='y_m', columns='x_m', values='B_T')
        B_grid = pivot.values
        dB_dx, dB_dy = np.gradient(B_grid, dx, dy)

        x_flat = X.flatten()
        y_flat = Y.flatten()
        jx_flat = jx.flatten()  # Плотность тока в А/м^2
        jy_flat = jy.flatten()
        j_flat = j.flatten()

        temp = pd.DataFrame({
            'title': name[:-4],
            'x': x_flat,
            'y': y_flat,
            'B': df['B'] * 1e-3,
            'dB_dx': dB_dx.flatten(),
            'dB_dy': dB_dy.flatten(),
            'Jc': j_flat,
            'Jx': jx_flat,
            'Jy': jy_flat
        })

        draw_Jc(temp)

        result_df = pd.concat([result_df, temp], ignore_index=True)

    result_df.to_csv(f'{output_path}/result.csv', index=False)

def compose_result():
    df_result = pd.read_csv("../../data/result.csv")
    vacs = [name for name in os.listdir("../parser/parsed_data/vac")]
    vac_features = []

    for vac in vacs:
        print(f"Composing {vac}")
        df_vac = pd.read_csv(f'../parser/parsed_data/vac/{vac}')
        title = str(df_vac["title"].iloc[0])
        print(f"title = {title}")
        Ic = extract_Ic(df_vac)
        print(f"Ic = {Ic}")
        Rn = extract_Rn(df_vac)
        print(f"Rn = {Rn}")
        n_exp = extract_power_law(df_vac)
        print(f"n_exp = {n_exp}\n")
        vac_features.append({"title": title, "Ic": Ic, "Rn": Rn, "n": n_exp})

    df_vac_features = pd.DataFrame(vac_features)
    merged = df_result.merge(df_vac_features, on="title", how="left")
    merged.to_csv("../../data/result_with_vac.csv", index=False)


def extract_Ic(df):
    U_threshold = 1e-6
    above = df[df["U"] >= U_threshold]
    return above["I"].min() if not above.empty else None

def extract_Rn(df, frac=0.2):
    tail = df.tail(int(len(df) * frac))
    coeffs = np.polyfit(tail["I"], tail["U"], 1)
    return coeffs[0]

def extract_power_law(df_vac):
    mask = (df_vac["I"] > 0) & (df_vac["U"] > 0)
    df = df_vac[mask]
    log_I = np.log(df["I"])
    log_U = np.log(df["U"])
    coeffs = np.polyfit(log_I, log_U, 1)
    return coeffs[0]

calculate_Jc('../parser/parsed_data/maps', '../../data')
compose_result()