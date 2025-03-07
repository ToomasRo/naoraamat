import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  photos: [],
  status: 'idle', // 'idle' | 'loading' | 'succeeded' | 'failed' | 'no-results'
};

const photoSearchSlice = createSlice({
  name: 'photoSearch',
  initialState,
  reducers: {
    setPhotos(state, action) {
      state.photos = action.payload;
    },
    setStatus(state, action) {
      state.status = action.payload;
    },
  },
});

export const { setPhotos, setStatus } = photoSearchSlice.actions;
export default photoSearchSlice.reducer;