import pprint
import re
import math
# oct qの変換


def oct2q(x):
    if x == 0:
        return math.inf  # 0の場合に分母が0になるので無限大を返す
    numerator = math.sqrt(2 ** x)
    denominator = 2 ** x - 1
    result = numerator / denominator
    return result
# optimod用時間をstereotool用時間に変換


def opti_att_ms_to_st_ms(ms):
    return (ms*4)


def opti_rel_ms_to_st_ms(ms):
    return (ms*2.5)
# dbを線形ゲインに変換


def db_to_linear_gain(dB):
    linear_gain = 10 ** (dB / 20)
    return linear_gain

# 線形ゲインをint16もどきの謎数値に変換


def linear_gain_to_int16(linear_gain):
    # int16に変換してスケール調整
    int16_gain = (linear_gain * 32768)
    return int16_gain

# dbをstereotoolで使用されるint16もどきの謎数値に変換


def db_to_st_gain(db):
    return round((linear_gain_to_int16(db_to_linear_gain(db))), 9)


def opti_db_to_st_gain(db):
    return db_to_st_gain(db/100)

# optimodの設定ファイルをdictに変換


def optimod_to_dict(input_string):
    lines = input_string.strip().split('\n')
    data_dict = {}
    current_key = None

    for line in lines:
        if line.startswith('OptimodVersion'):
            data_dict['OptimodVersion'] = line.split(
                '=')[1].strip().replace("<", "").replace(">", "")
        elif line.startswith('Preset Name'):
            preset_info = line.split(' ')
            data_dict['Preset Name'] = {
                'Name': preset_info[1].strip().replace("<", "").replace(">", "").replace("Name=", ""),
                'size': preset_info[2].strip().replace("size=", ""),
            }
        elif line.startswith('Factory Preset Name'):
            data_dict['Factory Preset Name'] = line.strip().replace(
                "<", "").replace(">", "").replace("Factory Preset Name=", "")
        elif line.startswith('Preset Type'):
            data_dict['Preset Type'] = line.split(
                '=')[1].strip().replace("<", "").replace(">", "")
        elif line.startswith('Preset File Name'):
            data_dict['Preset File Name'] = line.split(
                '=')[1].strip().replace("<", "").replace(">", "")
        elif 'String' in line:
            key_name = line.split(":")[1].strip().replace(
                "<", "").replace(">", "").replace("String", "")
            if ("RATIO" in key_name):
                line = line.split("<")
                line2 = line[2].split(";")
                data_dict[key_name] = {'value1': line2[0].replace(">", ""),
                                       'value2': (line2[1].replace("D:", "").replace(";", "")),
                                       'type': 'String',
                                       }
            else:
                line = line.split(":")
                data_dict[key_name] = {'value1': re.sub("<|>.*", "", line[2]),
                                       'value2': line[3].replace(";", ""),
                                       'type': 'String',
                                       }
        elif 'Int' in line:
            line = line.split(":")
            key_name = line[1].strip().replace(
                "<", "").replace(">", "").replace("Int", "")

            data_dict[key_name] = {'value1': int(re.sub("<|>.*|;D|;", "", line[2])),
                                   'value2': int(line[3].replace(";", "")),
                                   'type': 'Int',
                                   }
        elif 'Cent' in line:
            line = line.split(":")
            key_name = line[1].strip().replace(
                "<", "").replace(">", "").replace("Cent", "")
            data_dict[key_name] = {'value1': int(re.sub("<|>.*|;D|;", "", line[2])),
                                   'value2': int(line[3].replace(";", "")),
                                   'type': 'Cent',
                                   }
    return data_dict

# dictをoptimodの設定ファイルに変換


def dict_to_optimod(data_dict):
    lines = []

    # ヘッダー付与
    lines.append(f"OptimodVersion=<{data_dict['OptimodVersion']}>")
    lines.append(
        f"Preset Name=<{data_dict['Preset Name']['Name']}> size={data_dict['Preset Name']['size']}")
    lines.append(f"Factory Preset Name=<{data_dict['Factory Preset Name']}>")
    lines.append(f"Preset Type= <{data_dict['Preset Type']}>")
    lines.append(f"Preset File Name= <{data_dict['Preset File Name']}>")

    # データ付与
    for key, value in data_dict.items():
        if key not in ['OptimodVersion', 'Preset Name', 'Factory Preset Name', 'Preset Type', 'Preset File Name']:
            if value['type'] == 'String':
                if 'RATIO' in key:
                    line = f"C:<{key}>{value['type']}:<{value['value1']}>;D:{value['value2']};"
                else:
                    line = f"C:<{key}>{value['type']}:<{value['value1']}>;D:{value['value2']};"
            else:
                line = f"C:<{key}>{value['type']}:{value['value1']};D:{value['value2']};"
            lines.append(line)

    lines.append("End Preset<end>\n")

    return '\n'.join(lines)

# stereotoolの設定ファイルをdictに変換


def stereotool_to_dict(input_string):
    lines = input_string.strip().split('\n')
    data_dict = {}
    current_key = None

    for line in lines:
        if ("=" in line):
            line = line.split("=")
            if current_key not in data_dict:
                # Create an empty dictionary for the current key if it doesn't exist
                data_dict[current_key] = {}
            data_dict[current_key][line[0]] = line[1]
        else:
            key_name = line.replace("[", "").replace("]", "")
            current_key = key_name  # Update the current_key for subsequent lines

    return data_dict

# dictをstereotoolの設定ファイルに変換


def dict_to_stereotool(data_dict):
    output_lines = []

    for section, properties in data_dict.items():
        output_lines.append(f"[{section}]")
        for key, value in properties.items():
            output_lines.append(f"{key}={value}")
        output_lines.append("")  # Add an empty line between sections

    return '\n'.join(output_lines)


# ファイルからデータを読み込む
def read_data_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data_string = file.read()
    return data_string

# データをファイルに書き込む


def write_data_to_file(filename, data_string):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(data_string)


def convert_optimod_to_stereotool(input_name, base_sts_name, output_name):
    # それぞれの設定ファイルをdictに変換
    optimod_preset = optimod_to_dict(
        read_data_from_file(input_name))
    stereotool_preset = stereotool_to_dict(read_data_from_file(base_sts_name))

    # optimod設定項目をそれぞれの設定ファイルに変換
    # multiband thresholdを適用
    for band_num in range(1, 6):
        conf = "B" + str(band_num) + " COMP THRSH"
        stereotool_preset["Multiband Compressor 3"]["Threshold level band " + str(band_num)] = opti_db_to_st_gain(
            optimod_preset[conf]["value1"])

    # multiband attackを適用
    for band_num in range(1, 6):
        conf = "B" + str(band_num) + " ATTACK"
        stereotool_preset["Multiband Compressor 3"]["Attack (time to drop 86% in ms) band " + str(band_num)] = opti_att_ms_to_st_ms(
            optimod_preset[conf]["value1"])

    # multiband output gainを適用
    for band_num in range(1, 6):
        conf = "B" + str(band_num) + " OUTPUT MIX"
        stereotool_preset["Multiband Compressor 3"]["Output Level band " + str(band_num)] = db_to_linear_gain(
            optimod_preset[conf]["value1"]/100)

    # multiband releaseを適用
    release_time = 2000
    if (optimod_preset["MB RELEASE"] == 'Fast'):
        release_time = 200
    elif (optimod_preset["MB RELEASE"] == 'MFast'):
        release_time = 500
    elif (optimod_preset["MB RELEASE"] == 'Med2'):
        release_time = 1000
    elif (optimod_preset["MB RELEASE"] == 'Med'):
        release_time = 2000
    elif (optimod_preset["MB RELEASE"] == 'Slow2'):
        release_time = 4000
    elif (optimod_preset["MB RELEASE"] == 'Slow'):
        release_time = 8000
    for band_num in range(1, 6):
        conf = "B" + str(band_num) + " RELEASE"
        stereotool_preset["Multiband Compressor 3"]["Release (time to rise 10 dB in ms) band " + str(band_num)] = opti_rel_ms_to_st_ms(
            release_time)

    # couplingを適用
    stereotool_preset["Multiband Compressor 3"]["Band 2 coupling to band 3"] = optimod_preset["BAND 23 COUPL"]["value1"]/100
    stereotool_preset["Multiband Compressor 3"]["Band 3 coupling to band 2"] = optimod_preset["BAND 32 COUPL"]["value1"]/100
    stereotool_preset["Multiband Compressor 3"]["Band 3 coupling to band 4"] = optimod_preset["BAND 34 COUPL"]["value1"]/100
    stereotool_preset["Multiband Compressor 3"]["Band 4 coupling to band 5"] = optimod_preset["BAND 45 COUPL"]["value1"]/100
    # bririllianceを適用
    stereotool_preset["Multiband Compressor 3"]["Density drive band 5"] = db_to_linear_gain(
        optimod_preset["BRILLIANCE"]["value1"]/100)

    # AGCの設定を適用
    # attack
    # band1
    stereotool_preset["Pre Compressor"]["Bass Attack (time to drop 86%% in ms)"] = opti_att_ms_to_st_ms(
        optimod_preset["AGC BASS ATTACK"]["value1"]*10)
    # band2
    stereotool_preset["Pre Compressor"]["Attack (time to drop 86%% in ms)"] = opti_att_ms_to_st_ms(
        optimod_preset["AGC MASTER ATTACK"]["value1"]*10)

    # release
    # band1
    stereotool_preset["Pre Compressor"]["Release (time to rise 10 dB in ms)"] = opti_rel_ms_to_st_ms(
        optimod_preset["AGC RELEASE"]["value1"]*10)

    # band2
    stereotool_preset["Pre Compressor"]["Bass Release (time to rise 10 dB in ms)"] = opti_rel_ms_to_st_ms(
        optimod_preset["AGC BASS RELEASE"]["value1"]*10)

    # drive
    stereotool_preset["Pre Compressor"]["Drive"] = db_to_linear_gain(
        optimod_preset["AGC DRIVE"]["value1"])
    # イコライザーの設定を適用
    # LOW BASS
    # GAIN
    stereotool_preset["Equalizer"]["Parametric equalizer LF slope gain"] = db_to_linear_gain(
        optimod_preset["LOW BASS GAIN"]["value1"])
    # FREQ
    stereotool_preset["Equalizer"]["Parametric equalizer LF slope frequency"] = optimod_preset["LOW BASS FREQ"]["value1"]
    # Q
    stereotool_preset["Equalizer"]["Parametric equalizer LF slope"] = optimod_preset["LOW BASS Q"]["value1"]

    # PEQ LOW
    # GAIN
    stereotool_preset["Equalizer"]["Parametric equalizer gain 1"] = db_to_linear_gain(
        optimod_preset["PEQ LOW GAIN"]["value1"]/100)
    # FREQ
    stereotool_preset["Equalizer"]["Parametric equalizer frequency 1"] = optimod_preset["PEQ LOW FREQ"]["value1"]/100
    # Q
    stereotool_preset["Equalizer"]["Parametric equalizer Q 1"] = oct2q(
        optimod_preset["PEQ MID WIDTH"]["value1"]/100)

    # PEQ MID
    # GAIN
    stereotool_preset["Equalizer"]["Parametric equalizer gain 2"] = db_to_linear_gain(
        optimod_preset["PEQ MID GAIN"]["value1"]/100)
    # FREQ
    stereotool_preset["Equalizer"]["Parametric equalizer frequency 2"] = optimod_preset["PEQ MID FREQ"]["value1"]
    # Q
    stereotool_preset["Equalizer"]["Parametric equalizer Q 2"] = oct2q(
        optimod_preset["PEQ MID WIDTH"]["value1"]/100)

    # PEQ HIGH
    # GAIN
    stereotool_preset["Equalizer"]["Parametric equalizer gain 3"] = db_to_linear_gain(
        optimod_preset["PEQ HIGH GAIN"]["value1"]/100)
    # FREQ
    stereotool_preset["Equalizer"]["Parametric equalizer frequency 3"] = optimod_preset["PEQ HIGH FREQ"]["value1"]*10
    # Q
    stereotool_preset["Equalizer"]["Parametric equalizer Q 3"] = oct2q(
        optimod_preset["PEQ MID WIDTH"]["value1"]/100)

    # clipperの設定を適用(仕様の関係上-8db)
    stereotool_preset["Common"]["Extra loudness"] = db_to_linear_gain(
        optimod_preset["IBOC LIM DR"]["value1"]/100-8)

    # bass clipperの設定を適用
    if (optimod_preset["BASS CLIP"]["value1"] != "Off"):
        stereotool_preset["Bass Clipper"]["Threshold"] = db_to_linear_gain(
            optimod_preset["BASS CLIP"]["value1"]/100)
    write_data_to_file(output_name, dict_to_stereotool(stereotool_preset))


convert_optimod_to_stereotool(
    "presets/WMA MUSIC.orbf", "opti.sts", "WMA MUSIC.sts")
