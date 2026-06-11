import streamlit as st
import pandas as pd
import math
import os
import shutil
import tempfile
from io import BytesIO

st.set_page_config(
    page_title="Tách file Excel theo số dòng",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Tách file Excel theo số dòng")
st.write("Upload file Excel, nhập số dòng mỗi file, hệ thống sẽ tự tách và tạo file ZIP để tải về.")

# Upload file
uploaded_file = st.file_uploader(
    "Chọn file Excel",
    type=["xlsx", "xls"]
)

rows_per_file = st.number_input(
    "Nhập số dòng mỗi file",
    min_value=1,
    value=30,
    step=1
)

sheet_option = st.text_input(
    "Tên sheet hoặc số thứ tự sheet",
    value="0",
    help="Nhập 0 để lấy sheet đầu tiên, hoặc nhập tên sheet cụ thể"
)

if uploaded_file is not None:
    st.success(f"Đã upload file: {uploaded_file.name}")

    if st.button("🚀 Tách file Excel"):
        try:
            with st.spinner("Đang xử lý file..."):

                # Xử lý sheet
                if sheet_option.strip().isdigit():
                    sheet_name = int(sheet_option.strip())
                else:
                    sheet_name = sheet_option.strip()

                # Đọc Excel
                df = pd.read_excel(
                    uploaded_file,
                    sheet_name=sheet_name,
                    dtype=str
                )

                total_rows = len(df)
                total_files = math.ceil(total_rows / rows_per_file)

                if total_rows == 0:
                    st.warning("File Excel không có dữ liệu.")
                    st.stop()

                # Tạo thư mục tạm
                temp_dir = tempfile.mkdtemp()
                output_folder = os.path.join(temp_dir, "output_files")
                os.makedirs(output_folder, exist_ok=True)

                # Tách file
                created_files = []

                for i in range(total_files):
                    start_row = i * rows_per_file
                    end_row = start_row + rows_per_file

                    df_part = df.iloc[start_row:end_row]

                    output_file = os.path.join(
                        output_folder,
                        f"data_part_{i+1}.xlsx"
                    )

                    df_part.to_excel(output_file, index=False)
                    created_files.append(output_file)

                # Tạo file ZIP
                zip_path = os.path.join(temp_dir, "output_files")
                shutil.make_archive(zip_path, "zip", output_folder)

                final_zip_path = zip_path + ".zip"

                with open(final_zip_path, "rb") as f:
                    zip_data = f.read()

                st.success("✅ Hoàn tất tách file!")

                st.write(f"**Tổng số dòng:** {total_rows}")
                st.write(f"**Số dòng mỗi file:** {rows_per_file}")
                st.write(f"**Tổng số file đã tạo:** {total_files}")

                st.download_button(
                    label="⬇️ Tải file ZIP",
                    data=zip_data,
                    file_name="output_files.zip",
                    mime="application/zip"
                )

                with st.expander("Xem danh sách file đã tạo"):
                    for file in created_files:
                        st.write(os.path.basename(file))

        except Exception as e:
            st.error("Có lỗi xảy ra khi xử lý file.")
            st.exception(e)
