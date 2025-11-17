/**
 * Live rooms list screen.
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { api } from '../../services/api';
import { LiveRoom } from '../../types';

export default function LiveScreen({ navigation }: any) {
  const [rooms, setRooms] = useState<LiveRoom[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      const data = await api.getLiveRooms();
      setRooms(data);
    } catch (error) {
      console.error('Failed to load rooms:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadRooms();
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
        data={rooms}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListHeaderComponent={
          <View style={styles.header}>
            <TouchableOpacity
              style={styles.createButton}
              onPress={() => navigation.navigate('CreateRoom')}
            >
              <Text style={styles.createButtonText}>+ Yayın Başlat</Text>
            </TouchableOpacity>
          </View>
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>Henüz canlı yayın yok</Text>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.roomCard}
            onPress={() => navigation.navigate('Room', { roomId: item.id })}
          >
            <View style={styles.liveTag}>
              <Text style={styles.liveTagText}>🔴 CANLI</Text>
            </View>
            <Text style={styles.title}>{item.title}</Text>
            <Text style={styles.description}>{item.description}</Text>
            <View style={styles.hostInfo}>
              <Text style={styles.hostName}>{item.host.display_name}</Text>
              <Text style={styles.level}>{item.host.grill_level}</Text>
            </View>
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
  createButton: {
    backgroundColor: '#ff6b35',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  createButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
    paddingVertical: 40,
  },
  roomCard: {
    backgroundColor: '#2a2a2a',
    margin: 15,
    marginTop: 0,
    padding: 20,
    borderRadius: 12,
  },
  liveTag: {
    backgroundColor: '#ff0000',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 4,
    alignSelf: 'flex-start',
    marginBottom: 10,
  },
  liveTagText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  title: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    color: '#aaa',
    fontSize: 14,
    marginBottom: 15,
  },
  hostInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  hostName: {
    color: '#fff',
    fontSize: 14,
  },
  level: {
    color: '#ff6b35',
    fontSize: 12,
    fontWeight: 'bold',
  },
});
