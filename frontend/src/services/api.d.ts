export function findSeltsivend(first: string, last: string): Promise<{
  photos: Array<{
    last_name?: string;
    organisation?: string;
    created_at?: string;
    last_name?: string;
    first_name?: string;
    image_location?: string;
    face_location_in_image?: number[];
    version?: number;
    face_vector?: number[];
    scale_factor?: number;
  }>;
}>;

export function findSimilar(params: {
  face_vector?: number[];
}): Promise<{
  photos: Array<{
    last_name?: string;
    organisation?: string;
    created_at?: string;
    last_name?: string;
    first_name?: string;
    image_location?: string;
    face_location_in_image?: number[];
    version?: number;
    face_vector?: number[];
    scale_factor?: number;
  }>;
}>;

export function findSimilar(params: {
  first_name?: string;
  last_name?: string;
}): Promise<{
  photos: Array<{
    last_name?: string;
    organisation?: string;
    created_at?: string;
    last_name?: string;
    first_name?: string;
    image_location?: string;
    face_location_in_image?: number[];
    version?: number;
    face_vector?: number[];
    scale_factor?: number;
  }>;
}>;