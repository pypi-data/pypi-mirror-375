########################################################################################################################
## -- libraries and packages -- ########################################################################################
########################################################################################################################
import re
import wfdb
import pooch
import requests
import numpy as np
import pandas as pd
from importlib import resources

########################################################################################################################
## -- mimic iii waveform database data handler module -- ###############################################################
########################################################################################################################
class M3ValidationMasterClass():
  def __init__(self):
    super(M3ValidationMasterClass, self).__init__()

  def is_item_not_nan(self, batch_item: np.array) -> bool:
    return not np.isnan(batch_item).any()
  
  def is_length_valid(self, batch_item: np.array, sig_len: int) -> bool:
    return batch_item.shape[0] == sig_len

  def apply(self, batch_item: np.array, sig_len: int) -> bool:
    valid_flag = self.is_item_not_nan(batch_item = batch_item) and \
                 self.is_length_valid(batch_item = batch_item, sig_len = sig_len)
    return valid_flag

########################################################################################################################
## -- mimic iii waveform database data handler module -- ###############################################################
########################################################################################################################
class M3WaveFormMasterClass():
  def __init__(self) -> None:
    super(M3WaveFormMasterClass, self).__init__()
    with resources.open_binary("physioprep.data", "patient_signals.pkl") as file:
      patients_list_csv = pd.read_pickle(file)

    self.validation = M3ValidationMasterClass()
    self.args_preset = {
      "dat_cache_dir": pooch.os_cache('wfdb'),
      "physionet_url": "https://physionet.org/files/",
      "physionet_dir": "mimic3wdb-matched/1.0/",
      "patients_list": patients_list_csv,
    }

  ## -- get the list of patients from preset .csv or from physionet -- ##
  def get_patients(self, load_preset: bool = True) -> list[str]:
    if load_preset:
      patients_list = self.args_preset["patients_list"]
      patients_list = patients_list.apply(lambda r: f"{r['patient_group']}/{r['patient_id']}/", axis = 1).tolist()
      patients_list = set(patients_list)
    
    else:
      patients_url = self.args_preset["physionet_url"] + self.args_preset["physionet_dir"] + "RECORDS"
      patients_list = requests.get(patients_url).text.strip().split("\n")

    return list(patients_list)
  
  ## -- get the group and id for a single patient entry of form "pXX/pXXXXXX/" -- ##
  def get_patient_group_id(self, patient_group_id: str) -> tuple[str, str]:
    group, pid = re.match("([^/]+)/([^/]+)/", patient_group_id).groups()
    return group, pid

  ## -- get all the available signals -- ##
  def get_available_signals(self) -> list[str]:
    forbidden = ['???']
    unique_signals = self.args_preset["patients_list"]["patient_signals"].explode().dropna().unique()
    return [s for s in unique_signals if s not in forbidden]

  ## -- get patients that have the listed signals available -- ##
  def get_patient_with_signal(self, patients: list[str] | None = None, 
                              signal_filter: list[str] | None = None) -> pd.DataFrame:
    
    df = self.args_preset["patients_list"].copy()
    patients = patients if patients is not None else list(df["patient_id"])
    df = df[df["patient_id"].isin(patients)]
    if signal_filter is not None:
      df = df[df["patient_signals"].apply(lambda sig: set(signal_filter).issubset(sig))]
    return df

  ## -- get patient record as a dataset -- ##
  def get_patient_record(self, group: str, pid: str, record: str, sampfrom: int = 0, 
                         sampto: int | None  = None, channels: list[int] | None = None) -> wfdb.Record:

    df = self.args_preset["patients_list"].copy()
    available_channels = df[(df["patient_id"] == pid) & (df["patient_record"] == record)].iloc[0]
    channels = channels if channels is not None else available_channels["patient_signals"]
    channels = [available_channels["patient_signals"].index(item) for item in channels]
    pn_dir = self.args_preset["physionet_dir"] + group + "/" + pid
    rec = wfdb.rdrecord(record, pn_dir = pn_dir, sampfrom = sampfrom, sampto = sampto, channels = channels)
    return rec
  
  ## -- get patient record as a header -- ##
  def get_patient_header(self, group: str, pid: str, record: str) -> wfdb.Record:
    pn_dir = self.args_preset["physionet_dir"] + group + "/" + pid
    header = wfdb.rdheader(record, pn_dir = pn_dir)
    return header

  ## -- splits the available subjects into three separate dataframes for train, test, and validation -- ##
  def get_subject_split(self, df: pd.DataFrame, frac1: float = 0.8, frac2: float = 0.1, frac3: float = 0.1, 
                        seed: int | None = None, channels: list[str] | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    total = frac1 + frac2 + frac3
    frac1, frac2, frac3 = frac1/total, frac2/total, frac3/total
    df = self.get_patient_with_signal(patients = df["patient_id"], signal_filter = channels)
    df_shuffled = df.sample(frac = 1, random_state = seed).reset_index(drop = True)
    
    s1 = int(len(df) * frac1)
    s2 = int(len(df) * frac2)
    
    df1 = df_shuffled.iloc[:s1]
    df2 = df_shuffled.iloc[s1:s1+s2]
    df3 = df_shuffled.iloc[s1+s2:]
    
    return df1, df2, df3

  ## -- selects a random batch from the data -- ##
  def get_data_batch(self, df: pd.DataFrame, batch_size: int, signal_len: int, 
                     channels: list[str] | None = None, timeout: int = 100) -> np.array:

    batch, timeout_counter = [], 0
    timeout = max(batch_size, timeout)
    while len(batch) < batch_size and timeout_counter <= timeout:
      timeout_counter += 1 if len(batch) > 0 else 0
      rand_row = df.sample(n = 1).iloc[0]
      group, pid, record = rand_row["patient_group"], rand_row["patient_id"], rand_row["patient_record"]
      header = self.get_patient_header(group, pid, record)
      random_offset = np.random.randint(0, max(0, header.sig_len - signal_len) + 1)
      sampfrom, sampto = random_offset, random_offset + signal_len
      rec = self.get_patient_record(group, pid, record, sampfrom = sampfrom, sampto = sampto, channels = channels)
      waveform, val_flag = rec.p_signal, self.validation.apply(rec.p_signal, signal_len)
      batch.append(waveform.transpose(1, 0)) if val_flag else None
      # print(rec.p_signal.shape, header.fs, rec.sig_name)

    return np.stack(batch)