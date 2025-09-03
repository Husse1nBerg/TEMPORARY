'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

interface Store {
    id: number;
    name: string;
    status: string;
    last_scraped: string;
    total_products: number;
}

export default function StoresPage() {
    const [stores, setStores] = useState<Store[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStores = async () => {
            try {
                const data = await api.getStores();
                setStores(data);
            } catch (error) {
                console.error("Failed to fetch stores", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStores();
    }, []);

    const getStatusVariant = (status: string) => {
        switch (status.toLowerCase()) {
            case 'online': return 'default';
            case 'scraping': return 'secondary';
            case 'offline': return 'destructive';
            default: return 'outline';
        }
    };

    if (loading) return <p>Loading stores...</p>;

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold">Stores</h1>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Tracked Products</TableHead>
                        <TableHead>Last Scraped</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {stores.map((store) => (
                        <TableRow key={store.id}>
                            <TableCell className="font-medium">{store.name}</TableCell>
                            <TableCell>
                                <Badge variant={getStatusVariant(store.status)}>{store.status}</Badge>
                            </TableCell>
                            <TableCell>{store.total_products}</TableCell>
                            <TableCell>{store.last_scraped ? new Date(store.last_scraped).toLocaleString() : 'N/A'}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}