import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import DiscoveryBoard from './DiscoveryBoard'; // <-- Added import for your new component

const today = new Date().toISOString().split('T')[0];

export default function Home() {
    const navigate = useNavigate();
    const [searchForm, setSearchForm] = useState({ source: '', destination: '', date: '' });
    const [flights, setFlights] = useState([]);
    const [error, setError] = useState('');
    const [hasSearched, setHasSearched] = useState(false); // <-- Tracks if user initiated a search

    const handleSearch = async (e) => {
        e.preventDefault();
        setError('');
        setHasSearched(true); // <-- Hides the DiscoveryBoard when searching starts

        try {
            const response = await apiClient.get('flights/search/', { params: searchForm });
            if (response.data.flights.length === 0) {
                setError('No flights found for this route.');
            }
            
            setFlights(response.data.flights);
        } catch (err) {
            setError('Failed to fetch flights. Please check your inputs.');
            setFlights([]); // Clears old flights if an error occurs
        }
    };

    return (
        <div className="min-h-screen bg-creame px-6 py-12">
            <div className="max-w-5xl mx-auto">
                <div className="bg-pastelBlue p-8 rounded-2xl shadow-sm mb-10">
                    <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center"> Find your next flight </h1>
                    <form onSubmit={handleSearch} className="flex flex-row items-center gap-4 w-full" >
        
                        <input type="text" placeholder="Departure City" className="flex-1 min-w-[200px] p-4 rounded-xl outline-none focus:ring-2 focus:ring-julianna"
                         onChange={(e) => setSearchForm({...searchForm, source: e.target.value})} required />
            
                        <input type="text" placeholder="Arrival City" className="flex-1 min-w-[200px] p-4 rounded-xl outline-none focus:ring-2 focus:ring-julianna"
                         onChange={(e) => setSearchForm({...searchForm, destination: e.target.value})} required />
            
                        <input type="date" min={today} className="flex-1 min-w-[200px] p-4 rounded-xl outline-none focus:ring-2 focus:ring-julianna text-gray-700"
                         onChange={(e) => setSearchForm({...searchForm, date: e.target.value})} required />
            
                        <button type="submit" className="bg-julianna text-white px-8 py-4 rounded-xl font-bold hover:bg-opacity-90 transition-all whitespace-nowrap cursor-pointer" >
                        Search Flights
                        </button>
                     </form>
    
                    {error && <p className="text-red-500 mt-4 font-medium text-center">{error} </p>}
                </div>

                {/* --- CONDITIONAL RENDERING LOGIC --- */}
                <div className="space-y-6">
                    {!hasSearched ? (
                        <DiscoveryBoard />
                    ) : flights.length > 0 ? (
                        flights.map(flight => (
                            <div key={flight.id} className="bg-white p-6 rounded-2xl shadow-sm flex items-center justify-between border-l-4 border-addison" >
                                <div>
                                    <h3 className="text-xl font-bold text-gray-800"> {flight.airline} • {flight.flight_number} </h3>
                                    <p className="text-gray-600 mt-1">{flight.source} → {flight.destination} </p>
                                    <div className="flex gap-4 mt-3 text-sm font-medium text-gray-500">
                                        <span> Departs: {new Date(flight.departure_time).toLocaleTimeString()} </span>
                                        <span> Duration: {flight.duration} </span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm text-gray-500 mb-2"> {flight.available_seats} seats remaining </p>
                                    <button onClick={() => navigate(`/flight/${flight.id}/seats`)} className="bg-persimmon text-white px-6 py-2 rounded-lg font-semibold hover:opacity-90 cursor-pointer" >
                                    Select Seats
                                    </button>
                                </div>
                            </div>
                        ))
                    ) : null}
                </div>
            </div>
        </div>
    );
}