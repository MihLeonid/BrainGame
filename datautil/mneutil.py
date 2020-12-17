import sys
import time
import json
import struct
import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from mne.decoding import CSP

import mne
from mne.channels import read_layout

from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score

from mne.datasets import eegbci


CNT_CHANNELS = 4


if len(sys.argv) == 1:
    print("Usage: %s <session_name>" % sys.argv[0])
    raise SystemExit(0)


session_id = sys.argv[1].replace(".raw", "").replace(".json", "").replace("data/", "")

markers = []
markers_filename = "data/" + session_id + ".json"
data_filename = "data/" + session_id + ".raw"


all_data = []
with open(data_filename, "rb") as f:
    while True:
        block = f.read(8 * CNT_CHANNELS)
        if not block:
            break
        all_data.append(struct.unpack("<" + "d" * CNT_CHANNELS, block))
all_data = np.array(list(zip(*all_data)))

all_data /= 1000000  # uV to V


ch_types = ["eeg"] * CNT_CHANNELS
ch_names = BoardShim.get_eeg_names(BoardIds.SYNTHETIC_BOARD)[:CNT_CHANNELS]
sfreq = BoardShim.get_sampling_rate(BoardIds.SYNTHETIC_BOARD)


info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
raw = mne.io.RawArray(all_data, info)
raw.set_montage(mne.channels.make_standard_montage("standard_alphabetic"))

onset = []
duration = []
description = []
with open(markers_filename) as f:
    prev_marker = None
    for marker in json.loads(f.read()):
        onset.append(marker["start"] / sfreq)
        duration.append((marker["end"] - marker["start"]) / sfreq)
        description.append(marker["key"])

raw.set_annotations(mne.Annotations(onset=onset, duration=duration, description=description))
events, _ = mne.events_from_annotations(raw, event_id=lambda s: int(s))

raw.filter(7., 30., fir_design="firwin")

epochs = mne.Epochs(raw, events, proj=True, baseline=None, preload=True)
epochs.drop_bad()

labels = epochs.events[:, -1]

epochs_data = epochs.get_data()
cv = ShuffleSplit(10, test_size=0.2, random_state=42)
cv_split = cv.split(epochs_data)

csp = CSP(n_components=4, reg=None, log=True, norm_trace=False)
lda = LinearDiscriminantAnalysis()
clf = Pipeline([("CSP", csp), ("LDA", lda)])
scores = cross_val_score(clf, epochs_data, labels, cv=cv, n_jobs=1)

print(labels)
class_balance = np.mean(labels == labels[0])
class_balance = max(class_balance, 1. - class_balance)
print("Classification accuracy: %f / Chance level: %f" % (np.mean(scores), class_balance))

csp.fit_transform(epochs_data, labels)
csp.plot_patterns(epochs.info, ch_type='eeg', units='Patterns (AU)', size=1.5)



sfreq = raw.info['sfreq']
w_length = int(sfreq * 0.5)   # running classifier: window length
w_step = int(sfreq * 0.1)  # running classifier: window step size
w_start = np.arange(0, epochs_data.shape[2] - w_length, w_step)

scores_windows = []

for train_idx, test_idx in cv_split:
    y_train, y_test = labels[train_idx], labels[test_idx]

    X_train = csp.fit_transform(epochs_data[train_idx], y_train)
    X_test = csp.transform(epochs_data[test_idx])

    # fit classifier
    lda.fit(X_train, y_train)

    # running classifier: test classifier on sliding window
    score_this_window = []
    for n in w_start:
        X_test = csp.transform(epochs_data[test_idx][:, :, n:(n + w_length)])
        score_this_window.append(lda.score(X_test, y_test))
    scores_windows.append(score_this_window)

# Plot scores over time
w_times = (w_start + w_length / 2.) / sfreq + epochs.tmin

plt.figure()
plt.plot(w_times, np.mean(scores_windows, 0), label='Score')
plt.axvline(0, linestyle='--', color='k', label='Onset')
plt.axhline(0.5, linestyle='-', color='k', label='Chance')
plt.xlabel('time (s)')
plt.ylabel('classification accuracy')
plt.title('Classification score over time')
plt.legend(loc='lower right')
plt.show()



# for event_type in set(description):
#     evoked = epochs[event_type].average()
#     evoked.plot()

# raw.plot(events=events_from_annot, block=True)
# raw.plot(events=events, event_color={1: "red", 2: "blue", 3: "yellow", 4: "green", 5: "black", 6: "cyan", 7: "magenta", 8: "purple", 9: "pink", 0: "grass"}, block=True)
