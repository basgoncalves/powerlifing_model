import utils
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import opensim as osim
import os
import openSim
import ceinms

def find_non_zero_mom_arm_muscles(osim_model_path) -> list:
        '''
        Find the muscles that have non-zero moment arms in the given OpenSim model.
        '''
        
        # Load the OpenSim model
        model = osim.Model(osim_model_path)
        model.initSystem()

        coordinates = model.getCoordinateSet()

def add_joint_centres_to_trc(input_trc_path, output_trc_path=None, marker_map=None):
    """
    Add hip, knee, and ankle joint centre markers to a TRC file.

    New markers added (if computable):
      - RHJC, LHJC (hip joint centres)
      - RKJC, LKJC (knee joint centres)
      - RAJC, LAJC (ankle joint centres)
    """
    if output_trc_path is None:
        output_trc_path = input_trc_path.replace(".trc", "_with_JointCenters.trc")

    # -----------------------------
    # TRC read
    # -----------------------------
    with open(input_trc_path, "r") as f:
        lines = f.readlines()

    if len(lines) < 6:
        raise ValueError(f"Invalid TRC file: {input_trc_path}")

    header_1 = lines[0].rstrip("\n")
    header_keys = [x for x in lines[1].strip().split("\t") if x != ""]
    header_vals = [x for x in lines[2].strip().split("\t") if x != ""]

    marker_header = lines[3].rstrip("\n")
    coord_header = lines[4].rstrip("\n")

    df = pd.read_csv(input_trc_path, sep="\t", skiprows=5, header=None)

    marker_names = [m for m in marker_header.split("\t")[2:] if m.strip()]
    cols = ["Frame#", "Time"]
    for m in marker_names:
        cols.extend([f"{m}_X", f"{m}_Y", f"{m}_Z"])

    df = df.iloc[:, :len(cols)]
    df.columns = cols

    # -----------------------------
    # helpers
    # -----------------------------
    def has_marker(m):
        return all(c in df.columns for c in [f"{m}_X", f"{m}_Y", f"{m}_Z"])

    def get_marker_xyz(m):
        return df[[f"{m}_X", f"{m}_Y", f"{m}_Z"]].to_numpy(dtype=float)

    def set_marker_xyz(m, xyz):
        df[f"{m}_X"] = xyz[:, 0]
        df[f"{m}_Y"] = xyz[:, 1]
        df[f"{m}_Z"] = xyz[:, 2]

    def midpoint(m1, m2):
        return 0.5 * (get_marker_xyz(m1) + get_marker_xyz(m2))

    def first_valid_pair(pairs):
        for a, b in pairs:
            if has_marker(a) and has_marker(b):
                return a, b
        return None

    # -----------------------------
    # default marker map
    # -----------------------------
    default_map =  {
        "pelvis": {"LASI": "LASI", "RASI": "RASI", "LPSI": "LPSI", "RPSI": "RPSI"},
        "knee_r_pairs": [("RLFC", "RMFC"), ("RKNE", "RKNM"), ("RKNE", "RKNI"), ("RLK", "RMK")],
        "knee_l_pairs": [("LLFC", "LMFC"), ("LKNE", "LKNM"), ("LKNE", "LKNI"), ("LLK", "LMK")],
        "ankle_r_pairs": [("RANK", "RMED"), ("RANK", "RANM"), ("RANK", "RANKM"), ("RLA", "RMA")],
        "ankle_l_pairs": [("LANK", "LMED"), ("LANK", "LANM"), ("LANK", "LANKM"), ("LLA", "LMA")],
        "existing_hip_r": ["RHJC", "RHIP"],
        "existing_hip_l": ["LHJC", "LHIP"],
        }
    if marker_map is None:
        marker_map = default_map

    # -----------------------------
    # hip centres (Harrington-style pelvis-frame estimate)
    # -----------------------------
    rhjc_added = False
    lhjc_added = False

    # Use existing hip markers if present
    for m in marker_map["existing_hip_r"]:
        if has_marker(m):
            set_marker_xyz("RHJC", get_marker_xyz(m))
            rhjc_added = True
            break

    for m in marker_map["existing_hip_l"]:
        if has_marker(m):
            set_marker_xyz("LHJC", get_marker_xyz(m))
            lhjc_added = True
            break

    # If not available, estimate from pelvis landmarks
    pelvis = marker_map["pelvis"]
    if (not rhjc_added or not lhjc_added) and all(has_marker(pelvis[k]) for k in ["LASI", "RASI", "LPSI", "RPSI"]):
        LASI = get_marker_xyz(pelvis["LASI"])
        RASI = get_marker_xyz(pelvis["RASI"])
        LPSI = get_marker_xyz(pelvis["LPSI"])
        RPSI = get_marker_xyz(pelvis["RPSI"])

        mid_asis = 0.5 * (LASI + RASI)
        mid_psi = 0.5 * (LPSI + RPSI)

        # pelvis axes
        z_axis = RASI - LASI  # left -> right
        z_axis /= np.linalg.norm(z_axis, axis=1, keepdims=True)

        x_axis = mid_asis - mid_psi  # posterior -> anterior
        x_axis /= np.linalg.norm(x_axis, axis=1, keepdims=True)

        y_axis = np.cross(z_axis, x_axis)  # superior
        y_axis /= np.linalg.norm(y_axis, axis=1, keepdims=True)

        # re-orthogonalize x
        x_axis = np.cross(y_axis, z_axis)
        x_axis /= np.linalg.norm(x_axis, axis=1, keepdims=True)

        pelvis_width = np.linalg.norm(RASI - LASI, axis=1)   # mm
        pelvis_depth = np.linalg.norm(mid_asis - mid_psi, axis=1)  # mm

        # Harrington-like offsets (mm)
        x_post = -0.24 * pelvis_depth - 9.9
        y_inf = -0.30 * pelvis_width - 10.9
        z_lat = 0.33 * pelvis_width + 7.3

        # right(+z), left(-z)
        RHJC = mid_asis + x_axis * x_post[:, None] + y_axis * y_inf[:, None] + z_axis * z_lat[:, None]
        LHJC = mid_asis + x_axis * x_post[:, None] + y_axis * y_inf[:, None] - z_axis * z_lat[:, None]

        if not rhjc_added:
            set_marker_xyz("RHJC", RHJC)
        if not lhjc_added:
            set_marker_xyz("LHJC", LHJC)

    # -----------------------------
    # knee centres
    # -----------------------------
#     breakpoint()
    pair = first_valid_pair(marker_map["knee_r_pairs"])
    if pair is not None:
        set_marker_xyz("RKJC", midpoint(*pair))

    pair = first_valid_pair(marker_map["knee_l_pairs"])
    if pair is not None:
        set_marker_xyz("LKJC", midpoint(*pair))

    # -----------------------------
    # ankle centres
    # -----------------------------
    pair = first_valid_pair(marker_map["ankle_r_pairs"])
    if pair is not None:
        set_marker_xyz("RAJC", midpoint(*pair))

    pair = first_valid_pair(marker_map["ankle_l_pairs"])
    if pair is not None:
        set_marker_xyz("LAJC", midpoint(*pair))

    # -----------------------------
    # TRC write
    # -----------------------------
    out_marker_names = [c[:-2] for c in df.columns if c.endswith("_X")]
    num_markers = len(out_marker_names)

    # update header values
    header_map = dict(zip(header_keys, header_vals))
    if "NumFrames" in header_map:
        header_map["NumFrames"] = str(len(df))
    if "NumMarkers" in header_map:
        header_map["NumMarkers"] = str(num_markers)

    updated_vals = [header_map.get(k, "") for k in header_keys]
    line2 = "\t".join(header_keys) + "\n"
    line3 = "\t".join(updated_vals) + "\n"

    # marker + coord header
    line4_parts = ["Frame#", "Time"]
    for m in out_marker_names:
        line4_parts.extend([m, "", ""])
    line4 = "\t".join(line4_parts).rstrip() + "\n"

    line5_parts = ["", ""]
    for i in range(1, num_markers + 1):
        line5_parts.extend([f"X{i}", f"Y{i}", f"Z{i}"])
    line5 = "\t".join(line5_parts).rstrip() + "\n"

    with open(output_trc_path, "w") as f:
        f.write(header_1 + "\n")
        f.write(line2)
        f.write(line3)
        f.write(line4)
        f.write(line5)
        df.to_csv(f, sep="\t", index=False, header=False, float_format="%.6f", lineterminator="\n")

    print(f"Saved TRC with joint centres: {output_trc_path}")


if __name__ == "__main__":
        subject      = 'HC835B'
        session      = 'Session1'
        trials = ['HC835B_OGR_0002', 'HC835B_OGR_0003', 'HC835B_OGR_0004', 'HC835B_OGR_0005', 'HC835B_OGR_0006', 'HC835B_OGR_0007', 'HC835B_OGR_0008']


        for trial in trials:
                analysis = utils.Analyse(trialPath=os.path.join(utils.SIMULATIONS_DIR, subject, session, trial))

                # analysis.reset_settings_xml()
                # analysis._update_input_files()
                # analysis.reset_settings_xml()

                analysis.update_trial_attribute('replace', 'True')
                analysis.run_ik()
                breakpoint()
                analysis.run_id()
                analysis.run_ma()
                analysis.run_so()
                analysis.run_jra()



        