import colorsys
import os
import datetime
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

from constant import STATIC_DIR, ARCHETYPE_FILES_INFO
from pom_basic_information.pom_statistics import cal_dependency_type, cal_plugin_type, cal_plugins, cal_dependencies
from pom_basic_information.read_file import filter_pom_version, read_json_file
from pom_basic_information.version_compare import compare_item_add_del_in_all_pom


def get_jersey_vesion(pom_path):
    pom_file_dir = os.path.join(STATIC_DIR, pom_path)
    jersey_vesion = ""

    soup = BeautifulSoup(open(pom_file_dir, 'rt', encoding='latin1'), "xml")
    pom = soup.project
    if pom:
        jersey_vesion_pom = pom.find("jersey.version")
        if jersey_vesion_pom == None:
            jersey_vesion_pom = pom.find("jersey-version")
        if jersey_vesion_pom:
            jersey_vesion = jersey_vesion_pom.text
    if jersey_vesion:
        jersey_vesion = jersey_vesion.split("-")[0]
    return jersey_vesion


def get_pom_date(pom_path):
    pom_file_dir = os.path.join(STATIC_DIR, pom_path)
    current_time = time.localtime(os.path.getmtime(pom_file_dir))
    year = current_time.tm_year
    mon = current_time.tm_mon
    day = current_time.tm_mday
    return str(year) + "/" + str(mon) + "/" + str(day)


def get_jersey_time_version(pom_path):
    jersey_vesion = get_jersey_vesion(pom_path)
    if jersey_vesion:
        date = get_pom_date(pom_path)
        return [date, jersey_vesion]
    else:
        return None


def get_all_jersey_time_version(archetype_files_info_dict):
    all_pom_version_list = filter_pom_version(archetype_files_info_dict, True)
    num = 0
    jersey_version_list_all = []
    for one_pom_version_list in all_pom_version_list:
        length = len(one_pom_version_list)
        if length == 1:
            continue
        else:
            jersey_version_list = []
            for i in range(length - 1):
                pom1_path = one_pom_version_list[i]
                pom1_file_dir = os.path.join(STATIC_DIR, pom1_path)
                pom2_path = one_pom_version_list[i + 1]
                pom2_file_dir = os.path.join(STATIC_DIR, pom2_path)
                if pom1_path == pom2_path:
                    continue
                # print(pom1_file_dir, pom2_file_dir)
                if os.path.isfile(pom1_file_dir) and os.path.isfile(pom2_file_dir):
                    jersey1 = get_jersey_time_version(pom1_file_dir)
                    jersey2 = get_jersey_time_version(pom2_file_dir)
                    if i == 0 and jersey1:
                        jersey_version_list.append(jersey1)
                    if jersey1 and jersey2:
                        if jersey1[1] != jersey2[1]:
                            # print(jersey1, jersey2)
                            jersey_version_list.append(jersey2)
                            num += 1
            if len(jersey_version_list) > 0:
                jersey_version_list.append(pom1_path)
                print(pom1_path)
                jersey_version_list_all.append(jersey_version_list)
    print(num)
    return jersey_version_list_all


def get_digram_data(jersey_version_list_all):
    x1_list_all = []
    y1_list_all = []
    label1_list = []
    x2_list_all = []
    y2_list_all = []
    label2_list = []
    for data_list in jersey_version_list_all:
        x1_list = []
        y1_list = []
        x2_list = []
        y2_list = []
        for data in data_list[:-1]:
            time = data[0]
            version = data[1]
            version_major = float(version.split(".")[0])
            if version_major < 2:
                x1_list.append(time)
                y1_list.append(version)
            else:
                x2_list.append(time)
                y2_list.append(version)
        archetype_name = get_label_name(data_list[-1])
        if len(x1_list) > 0:
            x1_list_all.append(x1_list)
            y1_list_all.append(y1_list)
            label1_list.append(archetype_name)
        if len(x2_list) > 0:
            x2_list_all.append(x2_list)
            y2_list_all.append(y2_list)
            label2_list.append(archetype_name)
    return x1_list_all, y1_list_all, label1_list, x2_list_all, y2_list_all, label2_list


def get_label_name(archetype_name):
    label_name_list  = archetype_name.split("/")[1].split("=")
    label_name = label_name_list[-1]
    return label_name


def rand_hsl(h_total, h_idx):
    if h_total < 2:
        return 'blue'
    color_h = 0.65 / (h_total - 1) * h_idx
    color_l = 0.5
    color_s = 0.8
    rgb = colorsys.hls_to_rgb(color_h, color_l, color_s)
    return rgb

def format_version_list(version_list):
    new_version_list = []
    for version in version_list:
        new_version = format_version(version)
        new_version_list.append(new_version)
    return new_version_list


def format_version(version):
    return ".".join(version.split(".")[0:2])


def version2values(version):
    return [float(value) for value in version.split('.')]


def get_label2id(y_list_all):
    values = {}
    for y_list in y_list_all:
        for y in y_list:
            values[format_version(y)] = True
    values = values.keys()
    values = sorted(values, key=version2values)
    label2id = {value: idx + 1 for idx, value in enumerate(values)}
    return label2id


def draw_jersey_version_digram(x_list_all, y_list_all, label_list,fig_name,x_basic_list,y_basic_list):
    # date1 = ["2013/1/1", "2014/1/1", "2015/1/1" ,"2016/1/1", "2017/1/1", "2018/1/1", "2019/1/1"]
    # date2 = ["2008/1/1","2019/1/1",  "2010/1/1", "2011/1/1","2012/1/1"]
    # x1 = [datetime.strptime(d, '%Y/%d/%m').date() for d in date1]
    # x2 = [datetime.strptime(d, '%Y/%d/%m').date() for d in date2]
    # y1 = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19]
    # y2 =[2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.20, 2.21, 2.22, 2.23, 2.24, 2.25, 2.26, 2.27]
    plt.clf()
    length = len(x_list_all)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置时间标签显示格式
    y_list_all = [format_version_list(y_list) for y_list in y_list_all]
    label2id = get_label2id(y_list_all)
    # print(label2id)
    markers = ['v', '>', 'X', '^', '<', 'd', 'P']
    colors = ['#f5222d', '#fa8c16', '#fadb14', '#a0d911', '#faad14', '#1890ff', '#722ed1', '#eb2f96', '#13c2c2']
    for i in range(length):
        x_list = x_list_all[i]
        x_list = [datetime.datetime.strptime(d, '%Y/%m/%d').date() for d in x_list]
        y_list = [label2id[y] for y in y_list_all[i]]
        # print(x_list, y_list)
        plt.scatter(x_list, y_list, c=colors[i], marker=markers[i], alpha=0.6, s=40, label=label_list[i])

    plt.legend(fontsize=8)
    plt.yticks(list(label2id.values()), list(label2id.keys()))
    plt.gcf().autofmt_xdate()

    # #画jersey官方发布版本时间的折线
    ax = plt.gca()
    x_basic_list = [datetime.datetime.strptime(d, '%Y/%m/%d').date() for d in x_basic_list]
    y_basic_list = format_version_list(y_basic_list)
    basic_label2id = get_label2id([y_basic_list])
    y_basic_list = [basic_label2id[y] for y in y_basic_list]
    ax.plot(x_basic_list, y_basic_list, color='r', linewidth=1, alpha=0.6)
    # # plt.show()
    plt.savefig(fig_name)


def get_jersey_version_digram():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    jersey_version_list_all = get_all_jersey_time_version(archetype_files_info_dict)
    x1_list_all, y1_list_all, label1_list, x2_list_all, y2_list_all, label2_list = get_digram_data(jersey_version_list_all)
    y1_basic_list = ["1.0","1.1","1.2","1.3","1.4","1.5","1.6","1.7","1.8","1.9","1.10","1.11","1.12","1.13","1.14","1.15","1.16","1.17","1.18","1.19"]
    x1_basic_list = ["2008/10/13","2009/5/4","2010/5/10","2010/6/17","2010/9/11","2011/1/1","2011/3/1","2011/5/1","2011/6/1","2011/9/1","2011/11/1","2011/12/1","2012/2/1","2012/7/1","2012/9/1","2012/10/1","2012/12/1","2013/1/1","2013/11/5","2015/2/13"]
    y2_basic_list = [ "2.1","2.2","2.3", "2.4", "2.5", "2.6", "2.7", "2.8", "2.9", "2.10", "2.11", "2.12", "2.13", "2.14", "2.15", "2.16", "2.17", "2.18", "2.19", "2.20", "2.21", "2.22", "2.23", "2.24", "2.25", "2.26", "2.27", "2.28"]
    x2_basic_list = ["2013/7/15","2013/8/14","2013/9/20","2013/10/25","2013/11/18","2014/2/19","2014/3/13","2014/4/29","2014/5/23","2014/6/24","2014/7/23","2014/8/26","2014/9/26","2014/12/11","2015/1/14","2015/2/11","2015/3/11","2015/6/5","2015/6/29","2015/8/6","2015/8/17", "2015/9/23","2016/7/1","2016/8/27","2016/12/8","2017/9/6","2018/4/6","2019/1/25"]
    draw_jersey_version_digram(x1_list_all, y1_list_all, label1_list, "jersey1_version_change_test.pdf", x1_basic_list, y1_basic_list)
    draw_jersey_version_digram(x2_list_all, y2_list_all, label2_list, "jersey2_version_change_test.pdf", x2_basic_list, y2_basic_list)


def draw_digram(x_list_all, y_list_all, label_list):
    # date1 = ["2013/1/1", "2014/1/1", "2015/1/1" ,"2016/1/1", "2017/1/1", "2018/1/1", "2019/1/1"]
    # date2 = ["2008/1/1","2019/1/1",  "2010/1/1", "2011/1/1","2012/1/1"]
    # x1 = [datetime.strptime(d, '%Y/%d/%m').date() for d in date1]
    # x2 = [datetime.strptime(d, '%Y/%d/%m').date() for d in date2]
    # y1 = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19]
    # y2 =[2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14, 2.15, 2.16, 2.17, 2.18, 2.19, 2.20, 2.20, 2.21, 2.22, 2.23, 2.24, 2.25, 2.26, 2.27]
    plt.clf()
    length = len(x_list_all)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # 设置时间标签显示格
    markers = ['o', '+']
    colors = ['#002766', '#f5222d']
    for i in range(length):
        x_list = x_list_all[i]
        x_list = [datetime.datetime.strptime(d, '%Y/%m/%d').date() for d in x_list]
        y_list = y_list_all[i]
        plt.scatter(x_list, y_list, c=colors[i], alpha=0.5, s=1, label=label_list[i])

    plt.legend(fontsize=10)
    plt.gcf().autofmt_xdate()
    # plt.show()
    plt.savefig("dependency_delete_add.pdf")


def draw_bar_diagram(x_list_all, y_list_all, x_label_list_all, xlabel_name, ylabel_name, diagram_name, bar_color):
    # marks = ['/', ' \ ', '|',  '-', '+', 'x', 'o', 'O', '.', '*']
    plt.bar(x_list_all, y_list_all, color=bar_color, width=0.5)
    plt.xticks(x_list_all, x_label_list_all, rotation=35)
    plt.xlabel(xlabel_name)
    plt.ylabel(ylabel_name)
    plt.tight_layout()
    plt.savefig(diagram_name)


def draw_box_firgue(data_matrix, column_list, firgue_name,xlabel_name,ylabel_name):
    # plt.boxplot(data_matrix, labels=column_list, whis=1.5, meanline=True, showmeans=True,showfliers=False)
    # plt.boxplot(data_matrix, labels=column_list, whis=1.5,showmeans=True, showfliers=False)
    plt.boxplot(data_matrix, labels=column_list, whis=1.5)
    if xlabel_name:
        plt.xlabel(xlabel_name)
    if ylabel_name:
        plt.ylabel(ylabel_name)
    plt.tight_layout()
    plt.savefig(firgue_name)


def dependency_plugin_type_boxplt():
    dependency_type_num_list, feature_dict, dependency_num_20 = cal_dependency_type()
    dependency_max = np.max(dependency_type_num_list)
    dependency_type_num_list = [num for num in dependency_type_num_list if num < 75]
    plugin_type_num_list, feature_dict, plugin_num_20 = cal_plugin_type()
    plugin_max = np.max(plugin_type_num_list)
    plugin_type_num_list = [num for num in plugin_type_num_list if num < 100]
    data_matrix = [dependency_type_num_list, plugin_type_num_list]
    column_list = ["Dependency", "Plugin"]
    firgue_name ="d_p_type_box.pdf"
    draw_box_firgue(data_matrix, column_list, firgue_name, "", "Num for Type")


def dependency_plugin_num_boxplt():
    plugin_num_in_all_pom, plugin_feature_dict = cal_plugins()
    dependency_num_in_all_pom, dependency_feature_dict = cal_dependencies()
    data_matrix = [dependency_num_in_all_pom, plugin_num_in_all_pom]
    column_list = ["Dependency", "Plugin"]
    firgue_name = "d_p_num_box.pdf"
    draw_box_firgue(data_matrix, column_list, firgue_name, "", "Num in Pom")


def version_change_boxplt():
    archetype_files_info_dict = read_json_file(ARCHETYPE_FILES_INFO)
    dependency_del_num_list, dependency_add_num_list, plugin_del_num_list, plugin_add_num_list = compare_item_add_del_in_all_pom(archetype_files_info_dict, True)
    data_matrix = [dependency_del_num_list, dependency_add_num_list, plugin_del_num_list, plugin_add_num_list]
    column_list = ["Dependency Delete", "Dependency Add", "Plugin Delete", "Plugin Add"]
    firgue_name = "version_change_box.pdf"
    draw_box_firgue(data_matrix, column_list, firgue_name, "", "Num in Iteration")


def del_plu_change_iteration_bar_figure():
    x_list_all = [0, 1, 2, 3, 4, 5]
    y_list_all = [806, 582, 378, 246, 453, 151]
    x_label_list_all = ["Dependency Add", "Dependency Delete", "Plugin Add", "Plugin Delete", "Dependency Add and Delete", "Plugin Add and Delete"]
    draw_bar_diagram(x_list_all, y_list_all, x_label_list_all, "Version Change Type", "Iteration Num", "del_plu_change_iteration_num.pdf","#003a8c")


def high_tag(tag_type_name:str,bar_color):
    x_list_all = [0, 1, 2, 3, 4, 5]
    y_list_all = [5549, 3643, 5421, 3368, 13382, 7290]
    x_label_list_all = ["scope", "name", "configuration", "goal", "dependency", "plugin"]
    draw_bar_diagram(x_list_all, y_list_all, x_label_list_all, "Tag Name", "Number", tag_type_name,bar_color)

def version_change_bar_figuare():
    x_list_all = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    y_list_all = [3625, 2159, 2040, 1605, 1395, 705, 603, 399, 310, 246]
    x_label_list_all = ["dep_v", "plugin_v" ,"dep_add","dep_scope", "dep_del", "parent_v", "plugin_add", "plugin_del", "name", "properties_jersey-version"]
    draw_bar_diagram(x_list_all, y_list_all, x_label_list_all, "Version Change Type", "change Num", "version_change_all_num.pdf", "#135200")


if __name__ == "__main__":
    # x_list_all = [0,1,2,3,4,5,6,7]
    # y_list_all = [24484,22887,19116,13382,7290,5549,5421,5081,3643,3368]
    # x_label_list_all = ["artifactId","groupId","version","dependency","plugin","scope","configuration","id","name","goal"]
    # draw_bar_diagram(x_list_all,y_list_all,x_label_list_all,"top_tag_10.pdf")
    # y_list_all = [2061,2025,2026,2058,1684,1552,642,519]
    # x_label_list_all = ["artifactId", "groupId", "version", "modelVersion", "packaging", "name", "description","url"]
    # draw_bar_diagram(x_list_all, y_list_all, x_label_list_all, "top_tag_schema.pdf")
    # dependency_plugin_type_boxplt()
    # dependency_plugin_num_boxplt()
    # version_change_boxplt()
    # del_plu_change_iteration_bar_figure()
    # high_tag("top_tag_info.pdf","#a8071a")
    # version_change_bar_figuare()
    get_jersey_version_digram()

    # y_basic_list = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "1.9", "1.10", "1.11", "1.12",
    #                  "1.13", "1.14", "1.15", "1.16", "1.17", "1.18", "1.19"]
    # x_basic_list = ["2008/10/13", "2009/5/4", "2010/5/10", "2010/6/17", "2010/9/11", "2011/1/1", "2011/3/1",
    #                  "2011/5/1", "2011/6/1", "2011/9/1", "2011/11/1", "2011/12/1", "2012/2/1", "2012/7/1", "2012/9/1",
    #                  "2012/10/1", "2012/12/1", "2013/1/1", "2013/11/5", "2015/2/13"]
    #
    # ax = plt.gca()
    # x_basic_list = [datetime.datetime.strptime(d, '%Y/%m/%d').date() for d in x_basic_list]
    # y_basic_list = format_version_list(y_basic_list)
    # basic_label2id = get_label2id([y_basic_list])
    # y_basic_list = [basic_label2id[y] for y in y_basic_list]
    # ax.plot(x_basic_list, y_basic_list, color='r', linewidth=1, alpha=0.6)

