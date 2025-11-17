/**
 * Profile screen.
 */
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  Alert,
} from 'react-native';
import { useAuth } from '../../utils/AuthContext';

export default function ProfileScreen({ navigation }: any) {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    Alert.alert('Çıkış Yap', 'Çıkış yapmak istediğinizden emin misiniz?', [
      { text: 'İptal', style: 'cancel' },
      {
        text: 'Çıkış Yap',
        style: 'destructive',
        onPress: logout,
      },
    ]);
  };

  if (!user) return null;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Image
          source={{ uri: user.avatar_url || 'https://i.pravatar.cc/150' }}
          style={styles.avatar}
        />
        <Text style={styles.name}>{user.display_name}</Text>
        <Text style={styles.level}>{user.grill_level}</Text>
        {user.bio && <Text style={styles.bio}>{user.bio}</Text>}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Hesap Bilgileri</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>E-posta:</Text>
          <Text style={styles.infoValue}>{user.email}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Üyelik Tarihi:</Text>
          <Text style={styles.infoValue}>
            {new Date(user.created_at).toLocaleDateString('tr-TR')}
          </Text>
        </View>
      </View>

      <View style={styles.section}>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>📝 Profilimi Düzenle</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>📖 Tariflerim</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>❤️ Beğendiğim Tarifler</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.menuItem}>
          <Text style={styles.menuItemText}>⚙️ Ayarlar</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Text style={styles.logoutButtonText}>Çıkış Yap</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    alignItems: 'center',
    padding: 30,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  avatar: {
    width: 100,
    height: 100,
    borderRadius: 50,
    marginBottom: 15,
  },
  name: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  level: {
    color: '#ff6b35',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  bio: {
    color: '#aaa',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 10,
  },
  section: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  sectionTitle: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  infoLabel: {
    color: '#888',
    fontSize: 14,
  },
  infoValue: {
    color: '#fff',
    fontSize: 14,
  },
  menuItem: {
    backgroundColor: '#2a2a2a',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
  },
  menuItemText: {
    color: '#fff',
    fontSize: 16,
  },
  logoutButton: {
    backgroundColor: '#ff0000',
    margin: 20,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
