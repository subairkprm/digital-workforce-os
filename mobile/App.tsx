import { useState } from "react";
import { SafeAreaView, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";

export default function App() {
  const [signedIn, setSignedIn] = useState(false);
  if (!signedIn) return <SafeAreaView style={styles.screen}><View style={styles.card}><Text style={styles.brand}>DWCO</Text><Text style={styles.title}>Workforce login</Text><TextInput autoCapitalize="none" keyboardType="email-address" placeholder="Work email" style={styles.input}/><TextInput secureTextEntry placeholder="Password" style={styles.input}/><TouchableOpacity style={styles.button} onPress={() => setSignedIn(true)}><Text style={styles.buttonText}>Sign in</Text></TouchableOpacity></View></SafeAreaView>;
  return <SafeAreaView style={styles.screen}><View style={styles.card}><Text style={styles.title}>My profile</Text><Text>Employee profile placeholder</Text><View style={styles.rule}/><Text style={styles.title}>Directory</Text><Text>Tenant employee directory placeholder</Text></View></SafeAreaView>;
}

const styles = StyleSheet.create({screen:{flex:1,backgroundColor:"#eef3f9",justifyContent:"center",padding:24},card:{backgroundColor:"white",borderRadius:16,padding:24,gap:14},brand:{fontSize:14,fontWeight:"700",letterSpacing:3,color:"#3165a5"},title:{fontSize:26,fontWeight:"700",color:"#142440"},input:{borderColor:"#b8c5d5",borderWidth:1,borderRadius:8,padding:12},button:{backgroundColor:"#1d4f8d",borderRadius:8,padding:14,alignItems:"center"},buttonText:{color:"white",fontWeight:"700"},rule:{height:1,backgroundColor:"#dbe3ed",marginVertical:12}});
