import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setPhotos, setStatus } from './photoSearchSlice';
import { findSeltsivend, findSimilar } from '../../services/api';
import Switch from '@mui/material/Switch';
import FormControlLabel from '@mui/material/FormControlLabel';
import PhotoGrid from '../../components/PhotoGrid';
import { RootState } from '../../types/types';

import './PhotoSearchPage.css';



function PhotoSearchPage() {
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [searchError, setSearchError] = useState('');
    const [searchMode, setSearchMode] = useState<'exact' | 'similar'>('exact');


    const photos = useSelector((state: RootState) => state.photoSearch.photos);
    const status = useSelector((state: RootState) => state.photoSearch.status);
    const dispatch = useDispatch();

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!firstName.trim() || !lastName.trim()) {
            setSearchError('Please enter both first and last name');
            return;
        }

        setSearchError('');
        dispatch(setStatus('loading'));

        try {
            console.log("search mode on ", searchMode)
            const data = await (searchMode === 'exact'
                ? findSeltsivend(firstName, lastName)
                : findSimilar({first_name:firstName, last_name:lastName})
            )
            if (data && data.photos && data.photos.length > 0) {
                dispatch(setPhotos(data.photos));
                dispatch(setStatus('succeeded'));
            } else {
                dispatch(setPhotos([]));
                dispatch(setStatus('no-results'));
            }
        } catch (error) {
            console.error('Error searching for photos:', error);
            dispatch(setStatus('failed'));
            setSearchError('Failed to fetch photos. Please try again.');
        }
    };

    return (
        <div className="photo-search-container">
            <h1>Photo Search</h1>

            <form onSubmit={handleSearch} className="search-form">
                
                <div className="form-group">
                    <input
                        type="text"
                        placeholder="First Name"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        className="search-input"
                    />
                </div>
                <div className="form-group">
                    <input
                        type="text"
                        placeholder="Last Name"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        className="search-input"
                    />
                </div>

                <div className="search-mode-toggle">
                    <FormControlLabel
                        control={
                            <Switch
                                checked={searchMode === 'similar'}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchMode(e.target.checked ? 'similar' : 'exact')}
                                color="primary"
                            />
                        }
                        label={searchMode === 'exact' ? 'Exact Matches' : 'Similar Matches'}
                    />
                </div>
                <button type="submit" className="search-button">Search</button>
            </form>

            {searchError && <div className="error-message">{searchError}</div>}

            <div className="photo-gallery">
                {status === 'loading' && <div className="loading">Loading photos...</div>}

                {status === 'failed' && <div className="error-message">Failed to load photos. Please try again.</div>}

                {status === 'no-results' && <div className="no-results">No photos found for this person.</div>}

                {status === 'succeeded' && photos.length > 0 && (
                    <PhotoGrid photos={photos} firstName={firstName} lastName={lastName} />
                )}
            </div>
        </div>
    );
}

export default PhotoSearchPage;