import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { Ticket, Calendar, PlaneTakeoff, Armchair, Loader2, Plane, AlertCircle } from 'lucide-react';

export default function MyBookings() {
    const [bookings, setBookings] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [cancelModal, setCancelModal] = useState({ isOpen: false, bookingId: null });
    const [refundData, setRefundData] = useState(null);
    const [isProcessingCancel, setIsProcessingCancel] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchBookings();
    }, []);

    const fetchBookings = async () => {
        try {
            const res = await apiClient.get('my-bookings/'); 
            setBookings(res.data);
        } catch (err) {
            console.error(err);
            setError('Failed to load your trips. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };
    const handleCancelClick = async (bookingId) => {
        setCancelModal({ isOpen: true, bookingId });
        setRefundData(null);
        try {
            const res = await apiClient.get(`bookings/${bookingId}/refund-preview/`);
            setRefundData(res.data);
        } catch (err) {
            console.error("Failed to fetch refund preview", err);
            setRefundData({ error: "Could not calculate refund. Please try again." });
        }
    };
    const confirmCancellation = async () => {
        setIsProcessingCancel(true);
        try {
            await apiClient.post(`bookings/${cancelModal.bookingId}/cancel/`, { reason: "User requested cancellation" });
            setCancelModal({ isOpen: false, bookingId: null });
            setIsLoading(true);
            fetchBookings(); 
        } catch (err) {
            console.error("Failed to cancel", err);
            alert("Something went wrong while cancelling. Please try again.");
        } finally {
            setIsProcessingCancel(false);
        }
    };

    if (isLoading) return (
        <div className="min-h-[calc(100vh-80px)] bg-creame flex flex-col items-center justify-center">
            <Loader2 className="animate-spin text-julianna mb-4" size={48} />
            <p className="text-julianna font-bold text-xl tracking-wide">Retrieving your tickets...</p>
        </div>
    );

    if (error) return (
        <div className="min-h-[calc(100vh-80px)] bg-creame flex items-center justify-center px-4">
            <div className="text-center bg-white p-8 rounded-3xl shadow-xl">
                <p className="text-red-500 font-medium mb-4">{error}</p>
                <button onClick={fetchBookings} className="bg-julianna text-white px-6 py-2 rounded-xl font-bold shadow-md">Try Again</button>
            </div>
        </div>
    );

    return (
        <div className="min-h-[calc(100vh-80px)] bg-creame py-12 px-6 relative">
            <div className="max-w-5xl mx-auto">
                <div className="flex items-center gap-4 mb-10">
                    <div className="bg-white p-3 rounded-2xl text-julianna shadow-sm">
                        <Ticket size={32} />
                    </div>
                    <h1 className="text-4xl font-black text-gray-800 tracking-tight">My Trips</h1>
                </div>

                {bookings.length === 0 ? (
                    <div className="bg-white rounded-3xl p-12 text-center shadow-xl border-t-8 border-pastelBlue">
                        <Plane className="mx-auto text-gray-300 mb-6" size={64} />
                        <h2 className="text-2xl font-bold text-gray-800 mb-2">No upcoming flights</h2>
                        <p className="text-gray-500 mb-8 max-w-md mx-auto"> You havent made any booking.</p>
                        <button onClick={() => navigate('/')} className="bg-purple-700 text-white px-8 py-4 rounded-xl font-bold shadow-lg hover:-translate-y-1 transition-all">
                            Book a Flight
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {bookings.map((booking) => (
                            <div key={booking.id} className="bg-white rounded-3xl shadow-md overflow-hidden border border-gray-100 flex flex-col relative"> 
                                <div className="absolute top-4 right-4 bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider z-10">
                                    Confirmed
                                </div>
                                <div className="p-6 bg-gradient-to-br from-pastelBlue/10 to-transparent border-b border-dashed border-gray-200">
                                    <div className="flex justify-between items-center mb-4">
                                        <div className="flex items-center gap-2 text-julianna">
                                            <PlaneTakeoff size={20} />
                                            <span className="font-bold text-lg">{booking.flight.flight_number}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between mt-6">
                                        <div className="w-1/3">
                                            <p className="text-3xl font-black text-gray-800">{booking.flight.source.substring(0, 3).toUpperCase()}</p>
                                            <p className="text-sm text-gray-500 font-medium truncate">{booking.flight.source}</p>
                                        </div>
                                        <div className="w-1/3 flex flex-col items-center">
                                            <div className="w-full h-[2px] bg-gray-200 relative">
                                                <Plane className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-addison" size={16} />
                                            </div>
                                        </div>
                                        <div className="w-1/3 text-right">
                                            <p className="text-3xl font-black text-gray-800">{booking.flight.destination.substring(0, 3).toUpperCase()}</p>
                                            <p className="text-sm text-gray-500 font-medium truncate">{booking.flight.destination}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="p-6 bg-white flex justify-between items-end">
                                    <div className="space-y-4">
                                        <div>
                                            <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Passenger</p>
                                            <p className="font-bold text-gray-800">{booking.passenger_name}</p>
                                        </div>
                                        <div className="flex gap-6">
                                            <div>
                                                <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider flex items-center gap-1"><Calendar size={12}/> Date</p>
                                                <p className="font-bold text-gray-800">{booking.flight.departure_time.split('T')[0]}</p>
                                            </div>
                                        </div>
                                    </div>                                   
                                    <div className="flex flex-col items-end gap-3">
                                        <div className="bg-compassion/40 py-2 px-4 rounded-xl border border-addison/20 text-center min-w-[80px]">
                                            <p className="text-xs text-gray-500 font-semibold uppercase">Seat</p>
                                            <p className="text-lg font-black text-gray-900">{booking.seat.seat_number}</p>
                                        </div>
                                        <button onClick={() => handleCancelClick(booking.id)} className="text-xs font-bold text-red-500 hover:text-red-700 hover:underline transition-colors">
                                            Cancel Ticket
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            {cancelModal.isOpen && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-3xl max-w-md w-full p-8 shadow-2xl animate-in fade-in zoom-in duration-200">
                        <div className="flex items-center gap-3 text-red-500 mb-4">
                            <AlertCircle size={28} />
                            <h3 className="text-2xl font-black text-gray-900"> Cancel Flight? </h3>
                        </div>
                        {!refundData ? (
                            <div className="py-8 flex flex-col items-center justify-center space-y-3">
                                <Loader2 className="animate-spin text-julianna" size={32} />
                                <p className="text-sm font-medium text-gray-500"> Calculating your refund... </p>
                            </div>
                        ) : refundData.error ? (
                            <div className="py-4">
                                <p className="text-red-500">{refundData.error}</p>
                            </div>
                        ) : (
                            <div className="py-4 space-y-4">
                                <p className="text-gray-600 font-medium"> Are you sure you want to cancel this ticket? This action cannot be undone. </p>
                                <div className="bg-gray-50 p-4 rounded-2xl border border-gray-100" >
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-sm text-gray-500 font-bold"> Total Paid: </span>
                                        <span className="text-sm text-gray-500 line-through"> ₹{parseFloat(refundData.original_amount).toFixed(2)} </span>
                                    </div>
                                    <div className="flex justify-between items-center" >
                                        <span className="text-lg font-black text-gray-900"> Your Refund: </span>
                                        <span className="text-2xl font-black text-green-600"> ₹{parseFloat(refundData.refund_amount).toFixed(2)} </span>
                                    </div>
                                    <p className="text-xs text-center text-gray-400 mt-3 font-medium">
                                        Based on our {refundData.refund_percentage}% refund policy for this timeframe.
                                    </p>
                                </div>
                            </div>
                        )}
                        <div className="flex gap-3 mt-8">
                            <button onClick={() => setCancelModal({ isOpen: false, bookingId: null })} disabled={isProcessingCancel}
                                className="flex-1 py-3 px-4 rounded-xl font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50">
                                Keep Ticket
                            </button>
                            <button onClick={confirmCancellation} disabled={!refundData || refundData.error || isProcessingCancel}
                                className="flex-1 py-3 px-4 rounded-xl font-bold text-white bg-red-500 hover:bg-red-600 transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
                                {isProcessingCancel ? <Loader2 className="animate-spin" size={20} /> : "Yes, Cancel It"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}