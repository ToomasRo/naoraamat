import React from 'react';
import { Photo } from '../types/types';

interface PhotoCardProps {
    photo: Photo;
    index: number;
    firstName: string;
    lastName: string;
}

// TODO should fetch images from DB, but currently from local storage
const getImageSrc = (imagePath?: string): string => {
    if (!imagePath) return '';
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
    }
    try {
        if (imagePath.startsWith("data/reduced")) {
            imagePath = imagePath.replace("data/reduced/", "");
        }
        return `/public/photos/${imagePath}`;
    } catch (error) {
        console.error('Error loading image:', error);
        return '';
    }
};

const getGdriveLink = (gdrive_id?: string): string => {
    return `https://drive.google.com/file/d/${gdrive_id}/view`
}
const PhotoCard: React.FC<PhotoCardProps> = ({ photo, index, firstName, lastName }) => {
    return (
        <div className="photo-card">
            <a href={getGdriveLink(photo.gdrive_id)} target="_blank"><img
                src={getImageSrc(photo.image_location)}
                alt={`${firstName} ${lastName} - Photo ${index + 1}`}
                className="photo-image"
            /></a>
            {photo.created_at && (
                <div className="photo-metadata">
                    <span className="photo-date">{photo.created_at}</span>
                    {photo.organisation && <span className="photo-location">{photo.organisation}</span>}
                </div>
            )}
        </div>
    );
};

export default PhotoCard; 