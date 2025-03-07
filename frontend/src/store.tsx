import { configureStore } from '@reduxjs/toolkit';
import photoSearchReducer from './features/photoSearch/photoSearchSlice';
import annotationReducer from './features/faceAnnotation/annotationSlice';

export const store = configureStore({
  reducer: {
    photoSearch: photoSearchReducer,
    faceAnnotation: annotationReducer,
  },
});