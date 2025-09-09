import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from matplotlib.patches import Ellipse
import matplotlib
import re,sys,os

# 设置字体为 Arial
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['pdf.fonttype'] = 42  # 确保字体嵌入 PDF，不转换为路径

def plot_corr(matrix1, matrix2, label1, label2, **kwargs):
    import seaborn as sns
    import numpy as np
    import matplotlib.pyplot as plt

    fig_width = kwargs.get('fig_width', 6)
    fig_height = kwargs.get('fig_height', 6)
    dpi = kwargs.get('dpi', 300)
    corr_col = kwargs.get('corr_col', 'corr')
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=dpi)

    color1 = kwargs.get('color1', 'red')
    color2 = kwargs.get('color2', 'blue')

    # Create KDE plots for tumor and normal correlations
    sns.kdeplot(matrix1['corr'], fill=True, label=label1, ax=ax, color=color1)
    sns.kdeplot(matrix2['corr'], fill=True, label=label2, ax=ax, color=color2)

    # Compute medians
    median1 = np.nanmedian(matrix1['corr'])
    median2 = np.nanmedian(matrix2['corr'])

    # Plot vertical lines for medians
    short_label1 = kwargs.get('short_label1',label1[0])
    short_label2 = kwargs.get('short_label2',label2[0])

    ax.axvline(median1, color=color1, linestyle="--", label=f"{short_label1}: {median1:.2f}")
    ax.axvline(median2, color=color2, linestyle="--", label=f"{short_label2}: {median2:.2f}")

    # Add text annotations for medians
    ylim_top = ax.get_ylim()[1]  # Get the y-axis limit
    ax.text(median1 - 0.3, ylim_top * 0.8, f"{short_label1}: {median1:.2f}", ha='center', color=color1)
    ax.text(median2 - 0.3, ylim_top * 0.7, f"{short_label2}: {median2:.2f}", ha='center', color=color2)

    # Set title
    title = kwargs.get('title', 'Correlation Distribution')
    ax.set_title(title)

    # Show legend
    ax.legend()

    return fig, ax



def volcano(diff_df,s=5, hue='Significance', **kwargs):

    x_min = np.min(diff_df['Log2FC(median)'])
    x_max = np.max(diff_df['Log2FC(median)'])
    abs_x_max = max(abs(x_min), abs(x_max))
    x_min = -abs_x_max
    x_max = abs_x_max
    
    y_max = np.max(diff_df['-Log10(FDR)'])

    color_dict = {
        'NS': 'gray',
        'D': 'skyblue',
        'U': 'salmon',
        'S-D': 'blue',
        'S-U': 'red'
    }

    if hue == "GlycanType":
        color_dict = {
            "HM": "#1f77b4",      # Blue
            "only_F": "#ff7f0e",  # Orange
            "only_S": "#2ca02c",  # Green
            "F+S": "#d62728",     # Red
            "Other": "#9467bd"    # Purple
        }
    

    fig, ax = plt.subplots(figsize=(6,8))
    scatter = sns.scatterplot(data = diff_df, x = 'Log2FC(median)', y = '-Log10(FDR)', 
                    hue = hue,s=s, palette=color_dict)
    
    if 'annotations' in kwargs:
        uniq_map = dict()
        # print(kwargs['annotations'])
        for index,row in diff_df.iterrows():
            data_type = kwargs.get('data_type', 'glycosite')
            if data_type == 'glycosite':
                protein, gene, site,glycan = index.split("_")
                glycan = re.sub("[FSG]0","",glycan)
                key = f"{gene}_{site}_{glycan}"
            else:
                key = index
            x = float(row["Log2FC(median)"])
            y = float(row["-Log10(FDR)"])
   
            if key in kwargs['annotations']:
                if key in uniq_map:
                    uniq_map[key] += 1
                else:
                    uniq_map[key] = 1

        pos_map = dict()
        for index,row in diff_df.iterrows():
            data_type = kwargs.get('data_type', 'glycosite')
            if data_type == 'glycosite':
                protein, gene, site,glycan = index.split("_")
                glycan = re.sub("[FSG]0","",glycan)
                key = f"{gene}_{site}_{glycan}"
            else:
                key = index
            x = float(row["Log2FC(median)"])
            y = float(row["-Log10(FDR)"])
            if key in kwargs['annotations'] and uniq_map[key] == 1:
                pos_map[key] = (x,y)
                # print(key,glycan,index[3],index[2])

        y_values = [pos_map[key][1] for key in pos_map]
        y_values_sorted = sorted(y_values)
        # print(y_values_sorted)
        # print(np.min(y_values_sorted),np.max(y_values_sorted))

        old_y_max = np.max(y_values_sorted)
        old_y_min = np.min(y_values_sorted)
        # print(old_y_max,old_y_min)

        new_y_max = old_y_max + 1
        new_y_min = old_y_min - 5
        new_y_values = np.linspace(new_y_min, new_y_max, len(y_values_sorted))
        # print(new_y_values)
        y_mapping = {old_y: new_y for old_y, new_y in zip(y_values_sorted, new_y_values)}
        # print(y_mapping)

        old_y_range = old_y_max - old_y_min
        new_y_range = new_y_max - new_y_min

        new_pos_map = dict()

        for key in pos_map:
            x,y = pos_map[key]
            new_y = y_mapping[y]
            new_pos_map[key] = (x-2 if x < 0 else x + 2, new_y)


        for key in new_pos_map:
                x_text,y_text = new_pos_map[key]
                x,y = pos_map[key]
                
                if x < 0:
                    ax.text(x_text, y_text, key, ha='right',
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", 
                                facecolor="white", alpha=0.5))
                else:
                    ax.text(x_text, y_text, key, ha='left',
                            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", 
                                    facecolor="white", alpha=0.5))
                ax.annotate("",xy=(x,y),xytext=(x_text, y_text),ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", 
                              facecolor="white", alpha=0.5),
                              arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2", color="black"))


    
    # Add horizontal line at -log10(0.01)
    plt.axhline(y=-np.log10(0.01), color='black', linestyle='--', alpha=0.5)

    # Add vertical lines at log2(2) and -log2(2)
    plt.axvline(x=np.log2(2), color='black', linestyle='--', alpha=0.5)
    plt.axvline(x=-np.log2(2), color='black', linestyle='--', alpha=0.5)
   
    # Move the legend to the bottom right
    # ax.legend( loc='lower right')
    # Move the legend to the bottom right and set marker size and title
    from matplotlib.legend_handler import HandlerPathCollection
    legend = ax.legend(loc='lower right', title='Significance', prop={'size': 10},markerscale=3)
    # for handle in legend.legendHandles:
    #     handle._sizes = [30]  # Set marker size

    
    
    plt.ylim(0,y_max + 0.1)
    
    plt.xlim(x_min-6-0.1,x_max+6+0.1)

    return fig



def plot_enrichr_both(up_df,down_df,title,min_x=-10,max_x=10):
    rows = []
    for index,row in down_df.iterrows():
        d = row['Term']
        er = -1 * float(row['-Log10(Adj.P)'])
        c = 'S-D'
        rows.append([d + " ",er,c])
    for index,row in up_df.iterrows():
        d = row['Term']
        er = float(row['-Log10(Adj.P)'])
        c = "S-U"
        rows.append([" " + d,er,c])
    enrich_df = pd.DataFrame(rows,columns=['Term','-Log10(FDR)','Class']).sort_values('-Log10(FDR)',ascending=False)
    enrich_df['Original_Log10FDR'] = enrich_df['-Log10(FDR)']  # save original

    # enrich_df
    enrich_df['-Log10(FDR)'] = enrich_df['-Log10(FDR)'].map(lambda x: 20 if x > 20 else x)
    enrich_df['-Log10(FDR)'] = enrich_df['-Log10(FDR)'].map(lambda x: -20 if x < -20 else x)

    colors = ['red','blue']
    palette = sns.color_palette(colors)
    # palette = sns.color_palette("coolwarm", 2)
    
    sns.set_style('white')
    fig, ax = plt.subplots(figsize=(8,8),dpi=100)
    ax1 = sns.barplot(data=enrich_df,x='-Log10(FDR)',y='Term',hue='Class', palette=palette,)

    # --- Label bars with ORIGINAL values ---
    # Flatten the correct label list to match the actual drawing order
    label_list = enrich_df['Original_Log10FDR'].tolist()

    # Loop over each container and each bar in that container
    i = 0
    for container in ax1.containers:
        labels = [f'{label_list[i + j]:.1f}' for j in range(len(container))]
        ax1.bar_label(container, labels=labels, label_type='edge', padding=3)
        i += len(container)

    
    n = 0
    for index,row in enrich_df.iterrows():
        if row['-Log10(FDR)'] > 0:
            ax.text(-0.5,n+0.5, row['Term'],horizontalalignment = 'right', verticalalignment = 'bottom')
        else:
            ax.text(0.5,n+0.5, row['Term'],horizontalalignment = 'left', verticalalignment = 'bottom')
        n += 1
    plt.yticks([])
    plt.legend(bbox_to_anchor=(1,0.85))
    # t = ax.set_xticklabels(['','3','2','1','0','1','2',''])
    plt.xlim(min_x,max_x)
    plt.title(title)
    plt.ylabel('')

    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    # plt.plot([0,0],[-3,15],color='k',linewidth=0.5)
    plt.axvline(x=0,color='k',lw=0.5)
    plt.axhline(y=up_df.shape[0] + down_df.shape[0],color='k',lw=0.5)
    # plt.plot([min_x,max_x],[15,15],color='k',linewidth=0.5)
    # plt.tick_params(top='off', left='off', right='off', labelleft='off', labelbottom='on')
    plt.tight_layout(rect=[0, 0, 1, 0.95]) 
    return fig




def plot_pca(df, palette='Dark2',n=1, xlim=None, ylim=None,figsize=None):
    # np.random.seed(0)
    # df = pd.DataFrame({
    #     'PC1': np.random.randn(100),
    #     'PC2': np.random.randn(100),
    #     'PC3': np.random.randn(100),
    #     'PC4': np.random.randn(100),
    #     'Group': np.random.choice(range(1, 11), 100)
    # })
    
    # 假设最后一列是组别信息
    groups = list(df.iloc[:, -1])
    data = df.iloc[:, :-1]

    # 进行PCA分析
    pca = PCA(n_components=4)
    principalComponents = pca.fit_transform(data)

    df_pca = pd.DataFrame(data=principalComponents, columns=['PC1', 'PC2', 'PC3', 'PC4'])
    df_pca.index = data.index
    df_pca['Group'] = groups
    
    df_pca = df_pca.sort_values(by='Group')

    # 函数：绘制椭圆
    def plot_ellipse(x, y, ax,n_std=2.0, **kwargs):
        """
        Create a plot of the covariance confidence ellipse of *x* and *y*.

        Parameters
        ----------
        x, y : array-like, shape (n, )
            Input data.
        ax : matplotlib.axes.Axes
            The axes object to draw the ellipse into.
        n_std : float
            The number of standard deviations to determine the ellipse's radii.
        kwargs : dict
            Forwarded to `~matplotlib.patches.Ellipse`
        """
        if x.size != y.size:
            raise ValueError("x and y must be the same size")

        # cov = np.cov(x, y)
        # pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
        # ell_radius_x = np.sqrt(1 + pearson)
        # ell_radius_y = np.sqrt(1 - pearson)
        # ellipse = Ellipse((np.mean(x), np.mean(y)),
        #                 width=ell_radius_x * 2 * n_std,
        #                 height=ell_radius_y * 2 * n_std,
        #                 angle=np.rad2deg(np.arctan2(*np.linalg.eig(cov)[1][:, 0][::-1])),
        #                 **kwargs)
        cov = np.cov(x, y)
        mean_x = np.mean(x)
        mean_y = np.mean(y)
        lambda_, v = np.linalg.eig(cov)
        lambda_ = np.sqrt(lambda_)
        ellipse = Ellipse(xy=(mean_x, mean_y),
                    width=lambda_[0]*n_std*2, height=lambda_[1]*n_std*2,
                    angle=np.rad2deg(np.arctan2(*v[:, 0][::-1])),
                     **kwargs)


        ellipse.set_edgecolor(kwargs.get('edgecolor', 'black'))
        ellipse.set_facecolor('none')
        ax.add_patch(ellipse)
        return ellipse
    
    pc1_variance = pca.explained_variance_[0]  # 第一个特征值
    pc2_variance = pca.explained_variance_[1]  # 第一个特征值
    total_variance = sum(pca.explained_variance_)  # 总方差
    pc1_variance_ratio = pca.explained_variance_ratio_[0]  # PC1 解释的方差占比
    pc2_variance_ratio = pca.explained_variance_ratio_[1]  # PC1 解释的方差占比

    # 创建图形
    if n == 1:
        figsize = figsize if figsize is not None else (6, 8)
        fig, ax = plt.subplots(figsize=figsize, dpi=100)
        sns.scatterplot(data=df_pca, x='PC1', y='PC2', hue='Group', palette=palette, 
                        ax=ax, s=50, alpha=0.7, legend='full')
        # ax.set_xlim(-20,30)
        if xlim is not None:
            ax.set_xlim(xlim)
        if ylim is not None:
            ax.set_ylim(ylim)

        # 绘制椭圆
        print(list(df_pca['Group'].unique()))
        n_groups = len(df_pca['Group'].unique())
        for index, group in enumerate(sorted(list(df_pca['Group'].unique()))):
            group_data = df_pca[df_pca['Group'] == group]
            try:
                plot_ellipse(group_data['PC1'], group_data['PC2'], ax=ax, 
                            edgecolor=sns.color_palette(palette, n_groups)[index])
            except Exception as e:
                print(f"Error plotting ellipse for group {group}: {e}", file=sys.stderr)
                print(f"Group data: {group_data[['PC1', 'PC2']].head()}", file=sys.stderr)
                continue

        ax.set_xlabel(f'PC-1({pc1_variance_ratio*100:.2f}%)')
        ax.set_ylabel(f'PC-2({pc2_variance_ratio*100:.2f}%)')
    else:
        figsize = figsize if figsize is not None else (18, 12)
        fig, axes = plt.subplots(2, 3, figsize=figsize, dpi=100)

        pairs = [('PC1', 'PC2'), ('PC1', 'PC3'), ('PC1', 'PC4'), ('PC2', 'PC3'), ('PC2', 'PC4'), ('PC3', 'PC4')]
        for (ax, (pc_x, pc_y)) in zip(axes.flatten(), pairs):
            sns.scatterplot(data=df_pca, x=pc_x, y=pc_y, hue='Group', palette=palette, 
                            ax=ax, s=50, alpha=0.7, legend='full')

            # 绘制椭圆
            n_groups = len(df_pca['Group'].unique())
            for index, group in enumerate(sorted(list(df_pca['Group'].unique()))):
                group_data = df_pca[df_pca['Group'] == group]
                plot_ellipse(group_data[pc_x], group_data[pc_y], ax=ax, 
                            edgecolor=sns.color_palette(palette, n_groups)[index])

            ax.set_xlabel(pc_x)
            ax.set_ylabel(pc_y)

    plt.tight_layout()
    # plt.show()
    
    return fig, pca



def plot_volcano(diff_df,s=5, hue='Significance', **kwargs):

    x_min = np.min(diff_df['Log2FC(median)'])
    x_max = np.max(diff_df['Log2FC(median)'])
    abs_x_max = max(abs(x_min), abs(x_max))
    x_min = -abs_x_max
    x_max = abs_x_max
    
    y_max = np.max(diff_df['-Log10(FDR)'])

    color_dict = {
        'NS': 'gray',
        'D': 'skyblue',
        'U': 'salmon',
        'S-D': 'blue',
        'S-U': 'red'
    }

    if hue == "GlycanType":
        color_dict = {
            "HM": "#1f77b4",      # Blue
            "only_F": "#ff7f0e",  # Orange
            "only_S": "#2ca02c",  # Green
            "F+S": "#d62728",     # Red
            "Other": "#9467bd"    # Purple
        }
    

    fig, ax = plt.subplots(figsize=(8,8))
    scatter = sns.scatterplot(data = diff_df, x = 'Log2FC(median)', y = '-Log10(FDR)', 
                    hue = hue,s=s, palette=color_dict)
    
    if 'annotations' in kwargs:


        pos_map = dict()
        for index,row in diff_df.iterrows():
            if index in kwargs['annotations'] :       
                x = float(row["Log2FC(median)"])
                y = float(row["-Log10(FDR)"])
                pos_map[index] = (x,y)
                # print(key,glycan,index[3],index[2])

        y_values = [pos_map[key][1] for key in pos_map]
        y_values_sorted = sorted(y_values)
        # print(y_values_sorted)
        # print(np.min(y_values_sorted),np.max(y_values_sorted))

        old_y_max = np.max(y_values_sorted)
        old_y_min = np.min(y_values_sorted)
        # print(old_y_max,old_y_min)

        new_y_max = old_y_max + 1
        new_y_min = old_y_min - 5
        new_y_values = np.linspace(new_y_min, new_y_max, len(y_values_sorted))
        # print(new_y_values)
        y_mapping = {old_y: new_y for old_y, new_y in zip(y_values_sorted, new_y_values)}
        # print(y_mapping)

        old_y_range = old_y_max - old_y_min
        new_y_range = new_y_max - new_y_min

        new_pos_map = dict()

        for key in pos_map:
            x,y = pos_map[key]
            new_y = y_mapping[y]
            new_pos_map[key] = (x-2 if x < 0 else x + 2, new_y)


        for key in new_pos_map:
                x_text,y_text = new_pos_map[key]
                x,y = pos_map[key]
                data_type =  kwargs.get('data_type', 'glycosite') 
                if data_type == "glycosite":
                    protein, gene, site, glycan = key.split('_')
                    glycan = re.sub("[FSG]0","",glycan)
                    new_key = f"{gene}_{site}_{glycan}"
                elif data_type == "phosphosite":
                    gene_id, protein_id, site, sequence, _, gene = key.split('|')
                    new_key = f"{gene}_{site}"
                else:
                    new_key = key
                
                if x < 0:
                    ax.text(x_text, y_text, new_key, ha='right',
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", 
                                facecolor="white", alpha=0.5))
                else:
                    ax.text(x_text, y_text, new_key, ha='left',
                            bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", 
                                    facecolor="white", alpha=0.5))
                ax.annotate("",xy=(x,y),xytext=(x_text, y_text),ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", 
                              facecolor="white", alpha=0.5),
                              arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2", color="black", alpha=0.2))


    
    # Add horizontal line at -log10(0.01)
    plt.axhline(y=-np.log10(0.01), color='black', linestyle='--', alpha=0.5)

    # Add vertical lines at log2(2) and -log2(2)
    plt.axvline(x=np.log2(2), color='black', linestyle='--', alpha=0.5)
    plt.axvline(x=-np.log2(2), color='black', linestyle='--', alpha=0.5)
   
    # Move the legend to the bottom right
    # ax.legend( loc='lower right')
    # Move the legend to the bottom right and set marker size and title
    from matplotlib.legend_handler import HandlerPathCollection
    legend = ax.legend(loc='lower right', title='Significance', prop={'size': 10},markerscale=3)
    # for handle in legend.legendHandles:
    #     handle._sizes = [30]  # Set marker size

    
    xlim = kwargs.get('xlim', None)
    ylim = kwargs.get('ylim', None)

    if xlim is not None:
        plt.xlim(xlim)
    else:
        plt.xlim(x_min-11-0.1,x_max+11+0.1)

    if ylim is not None:
        plt.ylim(0,y_max + 0.1)
    else:
        plt.ylim(ylim)


    return fig

def venn2_diagram(set1, set2, label1, label2,
                  title="Venn Diagram of Red and Blue Glycosites",
                #   show=True, 
                  figsize=(4, 4), dpi=200):
    import matplotlib.pyplot as plt
    from matplotlib_venn import venn2
    from IPython.display import display  # Jupyter 下显示

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    vd = venn2([set1, set2], set_labels=(label1, label2), ax=ax)
    ax.set_title(title)

    # if show:            # 在 Jupyter 里显示
    #     display(fig)    # 或者：plt.show()

    return fig, ax, vd   # 返回图对象、坐标轴和 venn 对象，便于后续操作
