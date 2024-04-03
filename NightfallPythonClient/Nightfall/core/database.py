#database.py
import webbrowser
import pyodbc

def find_access_driver():
    for driver in pyodbc.drivers():
        if 'ACCESS' in driver.upper():
            return driver
    return None

#DATABASE Explaination
#DirTbl maps Direction strings to DirRefs (IDs) and Revids(reverse travel). And Dx,Dy,Dz gives information where this direction needs to be placed on the mapper (e,g, x+200 y-200 z=0)
#ExitKindTbl give information about doors that need to be opened when moving along a link. It contains a name (normal , door, locked door), a "Script" how to handle that (NULL, open door, unlock %1,open door)...
#ExitTbl the most important and biggest table. ExitIDs, ExitIdTo, FromID, ToID tell you how to travel. DirType is also relevant, cause this is the direction from DirTbl
#NoteTbl contains extra notes (strings) Only NoteID, ObjID and Note are relevant
#ObjectTbl the second most important table. Hoolds all the data about the rooms. ZoneID tells you in which Zone this room is.  X and Y how positions for the map (Coordinates), RefNumber and ObjId are the same identifier. Name is the first line of the room description and Desc contains the whole room description
#PortalTbl contains all portals, ways that can be entered from anywhere and cannot be drawn as such.
#ZoneTbl contains the Zones of the map. ZoneID references it Name is the caption. MinX MinY MaxX and MaxY show the total size of the zone. Dx and Dy the position and XOffset and YOffset how much they need to be movr to match upper and lower layers.X and Y seems to be the latest view center

db_file = r"C:\Program Files (x86)\zMUD\nightfall\Map\Map.mdb"
room_description_cache = {}
access_driver = (find_access_driver())

if access_driver is None:
    print("Microsoft Access Driver not found.")
    print("Please download and install the 64-bit Microsoft Access Database Engine 2016 Redistributable.")
    webbrowser.open("https://www.microsoft.com/en-us/download/details.aspx?id=54920")
else:
    conn_str = f'DRIVER={{{access_driver}}};DBQ={db_file}'

def open_db_connection():
    return pyodbc.connect(conn_str)

def fetch_zones():
    with open_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ZoneID, Name FROM ZoneTbl")
        zones = cursor.fetchall()
    return zones

def fetch_rooms(zone_id):
    with open_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ObjID, X, Y, Name FROM ObjectTbl WHERE ZoneID = ?", (zone_id,))
        rooms = cursor.fetchall()
    return rooms

def fetch_exits(from_obj_ids):
    with open_db_connection() as conn:
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in from_obj_ids)
        cursor.execute(f"SELECT FromID, ToID FROM ExitTbl WHERE FromID IN ({placeholders})", from_obj_ids)
        exits = cursor.fetchall()
    return exits
def fetch_room_description(room_id):
    if room_id in room_description_cache:
        return room_description_cache[room_id]

    with open_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Desc FROM ObjectTbl WHERE ObjID = ?", (room_id,))
        desc = cursor.fetchone()
        if desc:
            room_description_cache[room_id] = desc[0]
            return desc[0]