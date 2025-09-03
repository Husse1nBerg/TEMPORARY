'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface ProductDetails {
    id: number;
    name: string;
    category: string;
    is_organic: boolean;
    // Add other fields as needed
}

interface PriceTrend {
    date: string;
    price: number;
}

export default function ProductDetailPage({ params }: { params: { id: string } }) {
    const [product, setProduct] = useState<ProductDetails | null>(null);
    const [trends, setTrends] = useState<PriceTrend[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProductData = async () => {
            try {
                const productData = await api.getProduct(Number(params.id));
                setProduct(productData);

                const trendData = await api.getPriceTrends(Number(params.id), 30);
                setTrends(trendData);
            } catch (error) {
                console.error("Failed to fetch product data", error);
            } finally {
                setLoading(false);
            }
        };

        fetchProductData();
    }, [params.id]);

    if (loading) return <p>Loading product details...</p>;
    if (!product) return <p>Product not found.</p>;

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <Card>
                <CardHeader><CardTitle>Product Details</CardTitle></CardHeader>
                <CardContent>
                    <p><strong>Category:</strong> {product.category}</p>
                    <p><strong>Type:</strong> {product.is_organic ? 'Organic' : 'Conventional'}</p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader><CardTitle>30-Day Price Trend</CardTitle></CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={trends}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="price" stroke="#16a34a" activeDot={{ r: 8 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>
        </div>
    );
}