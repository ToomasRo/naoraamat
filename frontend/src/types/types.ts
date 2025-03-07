export interface Photo {
    last_name?: string;
    organisation?: string;
    created_at?: string;
    first_name?: string;
    image_location?: string;
    gdrive_id?: string;
    face_location_in_image?: number[];
    version?: number;
    face_vector?: number[];
    scale_factor?: number;
}

export interface RootState {
    photoSearch: {
        photos: Photo[];
        status: string;
    }
} 