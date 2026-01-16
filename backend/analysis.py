import os
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


def univariate_analysis(df, df_info, log_list=None):
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_cols) == 0:
        print("No numeric columns available for univariate analysis.")
        return

    print("\n=== UNIVARIATE ANALYSIS ===")
    print("Key descriptive statistics for numeric columns:\n")

    stats_df = df[numeric_cols].describe().T
    stats_df["skew"] = df[numeric_cols].skew().round(2)
    stats_df["%_zeros"] = (df[numeric_cols] == 0).mean().round(4) * 100
    stats_df = stats_df[
        ["count", "mean", "std", "min", "25%", "50%", "75%", "max", "skew", "%_zeros"]
    ]
    print(stats_df.to_string())

    if log_list is not None:
        nb_code = [
            "numeric_cols = df.select_dtypes(include=np.number).columns",
            "for col in numeric_cols:",
            "    fig, ax = plt.subplots(1, 2, figsize=(14, 5))",
            "    sns.histplot(df[col], kde=True, ax=ax[0])",
            "    ax[0].set_title(f'Dist of {col}')",
            "    sns.boxplot(x=df[col], ax=ax[1])",
            "    ax[1].set_title(f'Boxplot of {col}')",
            "    plt.show()",
        ]
        log_list.append(("Univariate Analysis", nb_code))

    try:
        print("\n" + "=" * 60)
        print("CHOOSE PLOT TYPES (you can select multiple)")
        print("=" * 60)
        print("1: Basic Plots Only (Histogram + Boxplot)")
        print("2: Histogram with KDE + Stats Overlay")
        print("3: Boxplot + Swarmplot")
        print("4: Violin Plot")
        print("5: QQ Plot")
        print("6: All of the above")
        print("Example: 1,3,5   or   2-4   or   6")

        attempts = 0
        selected_plots = set()
        while attempts < 3:
            user_input = input("\nYour choice: ").strip()
            if not user_input:
                attempts += 1
                print("Empty input not allowed.")
                continue

            temp_set = set()
            parts = [p.strip() for p in user_input.replace(" ", "").split(",")]
            valid = True
            for part in parts:
                if "-" in part:
                    try:
                        start, end = map(int, part.split("-"))
                        if 1 <= start <= end <= 6:
                            temp_set.update(range(start, end + 1))
                        else:
                            valid = False
                    except:
                        valid = False
                else:
                    try:
                        val = int(part)
                        if 1 <= val <= 6:
                            temp_set.add(val)
                        else:
                            valid = False
                    except:
                        valid = False

            if valid and temp_set:
                selected_plots = temp_set
                break
            else:
                attempts += 1
                print(f"Invalid selection. {3 - attempts} attempts left.")

        if not selected_plots:
            print("Too many invalid attempts. Defaulting to Basic Plots (1).")
            selected_plots = {1}

        if 6 in selected_plots:
            selected_plots = {1, 2, 3, 4, 5}

        print(f"\nSelected plot types: {sorted(selected_plots)}")

        print("\nChoose figure size:")
        print("1: Small (12x6)   2: Medium (16x8) - Recommended   3: Large (20x10)   4: Custom")
        size_choice = input("Enter choice (1-4): ").strip() or "2"
        if size_choice == "1":
            base_w, base_h = 12, 6
        elif size_choice == "3":
            base_w, base_h = 20, 10
        elif size_choice == "4":
            custom = input("Enter width,height (e.g., 18,10): ").strip()
            try:
                base_w, base_h = map(float, custom.split(","))
            except:
                base_w, base_h = 16, 8
        else:
            base_w, base_h = 16, 8

        folder = input("\nSave folder (Enter = current directory): ").strip() or "."
        os.makedirs(folder, exist_ok=True)
        print(f"All plots will be saved to: {os.path.abspath(folder)}")

        print("\n" + "=" * 50)
        print("VIEWING & SAVING MODE")
        print("=" * 50)
        print("1: View all plots one by one → save ALL at the end")
        print("2: Directly save all plots (no viewing)")
        print("3: View each plot → decide save individually")
        mode_input = input("Choose mode (1/2/3): ").strip() or "1"
        mode = mode_input if mode_input in ["1", "2", "3"] else "1"

        figures_to_save = []

        for col in numeric_cols:
            print(f"\nGenerating univariate plots for: {col}")

            mean_val = df[col].mean()
            median_val = df[col].median()
            skew_val = df[col].skew()
            zero_pct = (df[col] == 0).mean() * 100

            effective_num_plots = len(selected_plots)
            if 1 in selected_plots:
                effective_num_plots = max(effective_num_plots, 2)

            cols_per_row = min(effective_num_plots, 3)
            rows = (effective_num_plots + cols_per_row - 1) // cols_per_row

            fig_width = base_w * cols_per_row
            fig_height = base_h * rows

            fig, axes = plt.subplots(rows, cols_per_row, figsize=(fig_width, fig_height))

            if rows == 1 and cols_per_row == 1:
                axes = [axes]
            elif rows == 1:
                axes = list(axes)
            else:
                axes = axes.flatten().tolist()

            ax_idx = 0

            if 1 in selected_plots:
                ax = axes[ax_idx]
                df[col].hist(bins=50, ax=ax, color="skyblue", edgecolor="black", alpha=0.8)
                ax.set_title("Histogram")
                ax.set_xlabel(col)
                ax.set_ylabel("Frequency")
                ax.grid(alpha=0.3)
                ax_idx += 1

                ax = axes[ax_idx]
                df.boxplot(
                    column=col,
                    ax=ax,
                    patch_artist=True,
                    boxprops=dict(facecolor="lightcoral"),
                    medianprops=dict(color="black"),
                )
                ax.set_title("Boxplot")
                ax.grid(alpha=0.3)
                ax_idx += 1

            if 2 in selected_plots:
                ax = axes[ax_idx]
                df[col].hist(bins=50, ax=ax, color="lightblue", alpha=0.7, density=True)
                df[col].plot.density(ax=ax, color="red", linewidth=2, label="KDE")
                ax.axvline(mean_val, color="green", linestyle="--", label=f"Mean: {mean_val:.2f}")
                ax.axvline(
                    median_val,
                    color="orange",
                    linestyle="--",
                    label=f"Median: {median_val:.2f}",
                )
                ax.set_title(
                    f"Histogram + KDE\nSkew: {skew_val:.2f} | Zeros: {zero_pct:.1f}%"
                )
                ax.legend(fontsize=9)
                ax.grid(alpha=0.3)
                ax_idx += 1

            if 3 in selected_plots:
                ax = axes[ax_idx]
                sns.boxplot(y=df[col], ax=ax, color="lightblue")
                sns.swarmplot(y=df[col], ax=ax, color="black", alpha=0.5, size=3)
                ax.set_title("Boxplot + Swarmplot")
                ax_idx += 1

            if 4 in selected_plots:
                ax = axes[ax_idx]
                sns.violinplot(y=df[col], ax=ax, inner="quartile", color="lightgreen")
                ax.set_title("Violin Plot")
                ax_idx += 1

            if 5 in selected_plots:
                ax = axes[ax_idx]
                stats.probplot(df[col], dist="norm", plot=ax)
                ax.set_title("QQ Plot (vs Normal)")
                ax.grid(alpha=0.3)
                ax_idx += 1

            for j in range(ax_idx, len(axes)):
                axes[j].set_visible(False)

            plt.suptitle(f"Univariate Analysis: {col}", fontsize=16, fontweight="bold")
            plt.tight_layout(rect=[0, 0.03, 1, 0.95])

            figures_to_save.append((col, fig))

            if mode == "2":
                filename = f"{col.replace(' ', '_')}_univariate.png"
                path = os.path.join(folder, filename)
                fig.savefig(path, dpi=300, bbox_inches="tight")
                print(f"  Saved: {filename}")
                plt.close(fig)

            elif mode == "3":
                plt.show()
                save_this = input(f"Save plot for '{col}'? (y/n, Enter=y): ").strip().lower()
                if save_this != "n":
                    custom_name = input(
                        f"Filename (Enter = {col}_univariate.png): "
                    ).strip()
                    filename = (
                        custom_name if custom_name else f"{col.replace(' ', '_')}_univariate.png"
                    )
                    if not filename.endswith(".png"):
                        filename += ".png"
                    path = os.path.join(folder, filename)
                    fig.savefig(path, dpi=300, bbox_inches="tight")
                    print(f"  Saved: {path}")
                plt.close(fig)

            else:
                plt.show()
                plt.close(fig)

        if mode == "1" and figures_to_save:
            print("\n" + "=" * 50)
            print("All plots have been viewed.")
            save_all = input("Do you want to save ALL plots now? (y/n): ").strip().lower()
            if save_all == "y":
                for col, fig in figures_to_save:
                    filename = f"{col.replace(' ', '_')}_univariate.png"
                    path = os.path.join(folder, filename)
                    fig.savefig(path, dpi=300, bbox_inches="tight")
                    print(f"Saved: {filename}")
                print(f"\nAll plots saved to: {os.path.abspath(folder)}")

        print("\nUnivariate analysis completed successfully!")

    except ImportError as e:
        print(f"Required library missing: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def bivariate_analysis(df, df_info, log_list=None):
    print("\n" + "=" * 60)
    print("BIVARIATE ANALYSIS")
    print("=" * 60)

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    if len(numeric_cols) < 2:
        print("Not enough numeric columns for bivariate analysis.")
        return

    print("\nCorrelation types:")
    print("1: Pearson (linear correlation)")
    print("2: Spearman (rank correlation, good for non-linear/monotonic)")
    corr_type = input("Choose (1/2): ").strip() or "1"
    corr_method = "pearson" if corr_type == "1" else "spearman"

    pairplot_hue = None
    if df.select_dtypes(include=["object", "category"]).shape[1] > 0:
        print("\nCategorical columns available for hue in pairplot:")
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        for i, col in enumerate(cat_cols, 1):
            print(f"{i}: {col}")

        use_hue = input("\nUse a column as hue in pairplot? (y/n): ").strip().lower()
        if use_hue == "y":
            try:
                idx = int(input("Enter number (1-{}): ".format(len(cat_cols))).strip())
                pairplot_hue = cat_cols[idx - 1]
                print(f"Using '{pairplot_hue}' as hue.")
            except:
                print("Invalid selection. No hue will be used.")

    print("\nChoose figure size:")
    print("1: Small (12x10)   2: Medium (16x14)   3: Large (20x18)   4: Custom")
    size_choice = input("Choice (1-4): ").strip() or "2"
    if size_choice == "1":
        w, h = 12, 10
    elif size_choice == "3":
        w, h = 20, 18
    elif size_choice == "4":
        custom = input("width,height: ").strip()
        try:
            w, h = map(float, custom.split(","))
        except:
            w, h = 16, 14
    else:
        w, h = 16, 14

    folder = input("\nSave folder (Enter = current directory): ").strip() or "."
    os.makedirs(folder, exist_ok=True)
    print(f"All plots will be saved to: {os.path.abspath(folder)}")

    print("\n" + "=" * 50)
    print("VIEWING & SAVING MODE")
    print("=" * 50)
    print("1: View all plots → save ALL at the end")
    print("2: Directly save all plots (no viewing)")
    print("3: View each plot → decide save individually")
    mode_input = input("Choose mode (1/2/3): ").strip() or "1"
    mode = mode_input if mode_input in ["1", "2", "3"] else "1"

    figures_to_save = []

    if log_list is not None:
        nb_code = [
            "numeric_cols = df.select_dtypes(include=np.number).columns",
            "# Correlation Heatmap",
            f"plt.figure(figsize=({w}, {h}))",
            f"sns.heatmap(df[numeric_cols].corr(method='{corr_method}'), annot=True, cmap='coolwarm', fmt='.2f')",
            "plt.title('Correlation Matrix')",
            "plt.show()",
            "",
            "# Pairplot",
            f"sns.pairplot(df[numeric_cols], hue='{pairplot_hue}' if '{pairplot_hue}' != 'None' else None)",
            "plt.show()",
        ]
        log_list.append(("Bivariate Analysis", nb_code))

    print("\nGenerating Correlation Heatmap...")
    corr = df[numeric_cols].corr(method=corr_method)

    fig_heatmap, ax_heatmap = plt.subplots(figsize=(w, h))
    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        vmin=-1,
        vmax=1,
        linewidths=0.5,
        linecolor="white",
        ax=ax_heatmap,
    )
    ax_heatmap.set_title(f"Correlation Heatmap ({corr_method.capitalize()})", fontsize=16)
    plt.tight_layout()

    figures_to_save.append(("correlation_heatmap", fig_heatmap))

    if mode == "2":
        path = os.path.join(folder, "correlation_heatmap.png")
        fig_heatmap.savefig(path, dpi=300, bbox_inches="tight")
        print("  Saved: correlation_heatmap.png")
        plt.close(fig_heatmap)
    elif mode == "3":
        plt.show()
        save = input("Save heatmap? (y/n, Enter=y): ").strip().lower()
        if save != "n":
            path = os.path.join(folder, "correlation_heatmap.png")
            fig_heatmap.savefig(path, dpi=300, bbox_inches="tight")
            print("  Saved: correlation_heatmap.png")
        plt.close(fig_heatmap)
    else:
        plt.show()
        plt.close(fig_heatmap)

    print("\nGenerating Pairplot...")
    try:
        pairplot_fig = sns.pairplot(df[numeric_cols], diag_kind="kde", plot_kws={"alpha": 0.6}, hue=pairplot_hue)
        pairplot_fig.fig.suptitle("Pairplot of Numeric Features", y=1.02, fontsize=16)

        figures_to_save.append(("pairplot", pairplot_fig.fig))

        if mode == "2":
            path = os.path.join(folder, "pairplot.png")
            pairplot_fig.fig.savefig(path, dpi=300, bbox_inches="tight")
            print("  Saved: pairplot.png")
            plt.close(pairplot_fig.fig)
        elif mode == "3":
            plt.show()
            save = input("Save pairplot? (y/n, Enter=y): ").strip().lower()
            if save != "n":
                path = os.path.join(folder, "pairplot.png")
                pairplot_fig.fig.savefig(path, dpi=300, bbox_inches="tight")
                print("  Saved: pairplot.png")
            plt.close(pairplot_fig.fig)
        else:
            plt.show()
            plt.close(pairplot_fig.fig)
    except Exception as e:
        print(f"Could not generate pairplot: {e}")

    if mode == "1" and figures_to_save:
        print("\nAll plots have been viewed.")
        save_all = input("Do you want to save ALL plots now? (y/n): ").strip().lower()
        if save_all == "y":
            for name, fig in figures_to_save:
                filename = f"{name}.png"
                path = os.path.join(folder, filename)
                fig.savefig(path, dpi=300, bbox_inches="tight")
                print(f"Saved: {filename}")
            print(f"\nAll plots saved to: {os.path.abspath(folder)}")

    print("\nBivariate analysis completed successfully!")
