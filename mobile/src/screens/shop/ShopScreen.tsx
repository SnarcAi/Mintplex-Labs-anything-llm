/**
 * Shop screen - product catalog.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Image,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { api } from '../../services/api';
import { Product, ProductCategory } from '../../types';

export default function ShopScreen({ navigation }: any) {
  const [products, setProducts] = useState<Product[]>([]);
  const [category, setCategory] = useState<ProductCategory | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadProducts();
  }, [category]);

  const loadProducts = async () => {
    try {
      const data = await api.getProducts(category);
      setProducts(data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadProducts();
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={products}
        keyExtractor={(item) => item.id}
        numColumns={2}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.title}>MissYak Mağaza</Text>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.categoryScroll}
            >
              <TouchableOpacity
                style={[
                  styles.categoryButton,
                  !category && styles.categoryButtonActive,
                ]}
                onPress={() => setCategory(undefined)}
              >
                <Text
                  style={[
                    styles.categoryButtonText,
                    !category && styles.categoryButtonTextActive,
                  ]}
                >
                  Tümü
                </Text>
              </TouchableOpacity>
              {Object.values(ProductCategory).map((cat) => (
                <TouchableOpacity
                  key={cat}
                  style={[
                    styles.categoryButton,
                    category === cat && styles.categoryButtonActive,
                  ]}
                  onPress={() => setCategory(cat)}
                >
                  <Text
                    style={[
                      styles.categoryButtonText,
                      category === cat && styles.categoryButtonTextActive,
                    ]}
                  >
                    {cat}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.productCard}
            onPress={() =>
              navigation.navigate('ProductDetail', { productId: item.id })
            }
          >
            <Image source={{ uri: item.image_url }} style={styles.productImage} />
            <Text style={styles.productName} numberOfLines={2}>
              {item.name}
            </Text>
            <Text style={styles.productPrice}>
              {item.price} {item.currency}
            </Text>
          </TouchableOpacity>
        )}
      />
    </View>
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
  header: {
    padding: 20,
  },
  title: {
    color: '#fff',
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  categoryScroll: {
    marginBottom: 10,
  },
  categoryButton: {
    backgroundColor: '#2a2a2a',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
  },
  categoryButtonActive: {
    backgroundColor: '#ff6b35',
  },
  categoryButtonText: {
    color: '#888',
    fontSize: 14,
  },
  categoryButtonTextActive: {
    color: '#fff',
  },
  productCard: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    margin: 7.5,
    borderRadius: 12,
    overflow: 'hidden',
  },
  productImage: {
    width: '100%',
    height: 150,
  },
  productName: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    padding: 10,
    paddingBottom: 5,
  },
  productPrice: {
    color: '#ff6b35',
    fontSize: 16,
    fontWeight: 'bold',
    padding: 10,
    paddingTop: 0,
  },
});
