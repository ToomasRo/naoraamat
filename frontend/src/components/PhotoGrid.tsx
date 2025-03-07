import React from 'react';
import PhotoCard from './PhotoCard';
import { Photo } from '../types/types';

interface PhotoGridProps {
    photos: Photo[];
    firstName: string;
    lastName: string;
}

const PhotoGrid: React.FC<PhotoGridProps> = ({ photos, firstName, lastName }) => {
    return (
        <div className="photos-grid">
            {photos.map((photo: Photo, index: number) => (
                <PhotoCard
                    key={index}
                    photo={photo}
                    index={index}
                    firstName={firstName}
                    lastName={lastName}
                />
            ))}
        </div>
    );
};

export default PhotoGrid; 