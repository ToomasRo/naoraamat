# Project Summary

## How to Run the Project

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/seltsi_naoraamat.git
    cd seltsi_naoraamat
    ```

2. **Create a Virtual Environment:**
    ```bash
    cd backend
    virtualenv venv
    ```

3. **Install Dependencies:**
    ```bash
    pipenv install -r requirements.txt
    ```

4. **Run the Application:**
    ```bash
    docker compose up
    ```

5. **Access the Application:**
    Open your web browser and go to `http://localhost:8000`.
    Kibana lives on `http://127.0.0.1:5601/`.

## Additional Information
Work in progress

## TODO list

- [ ] Laadida pildid semestritest 2020-II kuni 2024-I kausta `backend\data\pildid\{semester}`
- [ ] Skript mis võtab pildi, kasutab resize2fullhd ja asetab pildi kausta `backend\data\pildid\reduced\{semester}`
- [ ] Viia kokku gdriveID ja pildi path kasutades selleks tõenäoliselt `utils\grdive_integration.py`
- [ ] reduced pildid laadida üles 'unnanmed-index'. Vaja et sisalduks igas kirjes:
    - Need vaja üleval pool koos hoida
    ```python
    properties = {
            "face_vector": {'type': 'dense_vector', 'dims': 128},
            "face_location_in_image": {"type": "keyword"},

            "image_path": {"type": "text"},             # asukoht arvutis
            "scale_factor": {"type": "float"},          # kui palju selle väiksemaks tegime
            "gdrive_id": {"type": "text"},              # id mille abil saab selle drivest https://drive.google.com/file/d/{gid}/view
            "version": {"type": "long"},                # see et mis DB skeemaga see index tehtud on 
                }
    ```