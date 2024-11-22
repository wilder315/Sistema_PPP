import pymysql

def obtener_conexion():
    try:
        conexion = pymysql.connect(
            host='junction.proxy.rlwy.net',
            port=28269,
            user='root',
            password='dvIcHQBFZrICrloweOguVmZkHcoVluEA',
            db='bd_ppp'
        )
        print("Conexión exitosa a la base de datos.")
        return conexion
    #junction.proxy.rlwy.net:28269
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None 
