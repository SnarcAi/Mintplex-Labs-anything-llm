/**
 * Product detail screen.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Image,
  TouchableOpacity,
  ActivityIndicator,
  Linking,
} from 'react-native';
import { api } from '../../services/api';
import { Product } from '../../types';

export default function ProductDetailScreen({ route }: any) {
  const { productId } = route.params;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProduct();
  }, []);

  const loadProduct = async () => {
    try {
      const data = await api.getProduct(productId);
      setProduct(data);
    } catch (error) {
      console.error('Failed to load product:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBuyNow = () => {
    if (product?.external_url) {
      Linking.openURL(product.external_url);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
      </View>
    );
  }

  if (!product) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.errorText}>Ürün bulunamadı</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Image source={{ uri: product.image_url }} style={styles.image} />

      <View style={styles.content}>
        <View style={styles.categoryTag}>
          <Text style={styles.categoryText}>{product.category}</Text>
        </View>

        <Text style={styles.title}>{product.name}</Text>

        <Text style={styles.price}>
          {product.price} {product.currency}
        </Text>

        <Text style={styles.description}>{product.description}</Text>

        <TouchableOpacity style={styles.buyButton} onPress={handleBuyNow}>
          <Text style={styles.buyButtonText}>🛒 Satın Al</Text>
        </TouchableOpacity>

        <Text style={styles.note}>
          Satın alma işlemi MissYak.com üzerinden gerçekleştirilecektir.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: '#fff',
    fontSize: 16,
  },
  image: {
    width: '100%',
    height: 300,
  },
  content: {
    padding: 20,
  },
  categoryTag: {
    backgroundColor: '#2a2a2a',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginBottom: 15,
  },
  categoryText: {
    color: '#ff6b35',
    fontSize: 12,
    fontWeight: 'bold',
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  price: {
    color: '#ff6b35',
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  description: {
    color: '#ccc',
    fontSize: 16,
    lineHeight: 24,
    marginBottom: 30,
  },
  buyButton: {
    backgroundColor: '#ff6b35',
    padding: 18,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 15,
  },
  buyButtonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  note: {
    color: '#888',
    fontSize: 14,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});
