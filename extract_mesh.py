import sys
import struct

major = 1
minor = 1

filename = sys.argv[1]
asset_file = open(filename, 'r')
LINES = asset_file.readlines()

obj_filename = filename.split(".")[0] + ".obj"
mtl_filename = filename.split(".")[0] + ".mtl"

vertex_count = 0
index_count = 0
mesh_name = ""
print("Solar Smash Unity Tools Asset Extractor v." + str(major) + "." + str(minor))

index_buffer_flag = 0
vertex_buffer_flag = 0

vertex_buffer = []
index_buffer = []

for line in LINES:

    if "1 string m_Name" in line:
        mesh_name = str(line.split("=")[1].strip().strip('"'))
        print("Mesh Name: " + mesh_name)

    #Extract Vertex Count
    elif "vertexCount" in line:
        vertex_count = int(line.split("=")[1].strip())
        print("Vertex Count: " + str(vertex_count))

    #Extract Index Count    
    elif "indexCount" in line:
        index_count = int(line.split("=")[1].strip())
        print("Index Count: " + str(index_count)) 



    ###########################################
    #Extract Index Buffer
    
    elif "0 vector m_IndexBuffer" in line:
        print("Extracting Index Buffer...", end = '')
        index_buffer_flag = 1

    #Extract Index Buffer, stored as 4-Byte Word in Big-Endian so we swap Byte 0 and 1 for each work.
    #Example index 9 would be stored as 0900. Swap 09 and 00 => 0009
    elif index_buffer_flag > 0 and "0 UInt8 data" in line:
        if index_buffer_flag == 1:
            low_byte = int(line.split("=")[1])
            index_buffer_flag = 2
        
        elif index_buffer_flag == 2:
            high_byte = int(line.split("=")[1])
            index_buffer_flag = 1
            #if(high_byte > 0):
                #low_byte+=1
            
            index_buffer.append(int(low_byte + (high_byte * 256)) +1)


    elif "1 VertexData m_VertexData" in line:
        index_buffer_flag = 0

        print("Done")

    #End Extract Index Buffer
    ###########################################


    ###########################################
    #Extract Vertex Buffer
    
    elif "1 TypelessData m_DataSize" in line:
        print("Extracting Vertex Buffer...", end = '')
        vertex_buffer_flag = 1

    #Extract Vertex Buffer Data
    elif vertex_buffer_flag == 1 and "0 UInt8 data" in line:
        vertex_buffer.append(int(line.split("=")[1]))
            


    elif "0 CompressedMesh m_CompressedMesh" in line:
        vertex_buffer_flag = 0
        print("Done")

    #End Extract Index Buffer
    ###########################################


print("Index Buffer Size: " + str(len(index_buffer)))
print("Vertex Buffer Size: " + str(len(vertex_buffer)))


#Validate data

#Check Index Buffer for triangles

if len(index_buffer)%3 == 0:
    print("Triangular Mesh Detected")
else:
    print("Square Mesh Detected")


print("VERTEX PACKET SIZE: " + str(int(len(vertex_buffer)/vertex_count) ))
size = int(len(vertex_buffer)/vertex_count)

for i in range(0,size):
    print("Byte[" + str(i) + "]: " + str(vertex_buffer[i]))




    ###########################################
    #Create Object File


uv_filename = ""
uv_material_name = mesh_name + "_uv_map"

obj_file = open(obj_filename, "w+")

obj_file.write("# Blender v2.91.2 OBJ File: ''\n")
obj_file.write("#Solar Smash Unity Tools v." + str(major) + "." + str(minor)+ "\n")
#obj_file.write("mtllib cube.mtl\n")
obj_file.write("o " + mesh_name + "\n")

#Write Vertex
for index in range(int( len(vertex_buffer) / (len(vertex_buffer)/vertex_count) ) ):
    temp = "{:02x}".format(vertex_buffer[(index*size)+0]) + "{:02x}".format(vertex_buffer[(index*size)+1]) + "{:02x}".format(vertex_buffer[(index*size)+2]) + "{:02x}".format(vertex_buffer[(index*size)+3])
    #print(str(temp))
    vertex1 = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6))
    
    temp = "{:02x}".format(vertex_buffer[(index*size)+4]) + "{:02x}".format(vertex_buffer[(index*size)+5]) + "{:02x}".format(vertex_buffer[(index*size)+6]) + "{:02x}".format(vertex_buffer[(index*size)+7])
    #print(str(temp))
    vertex2 = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6))
    
    temp = "{:02x}".format(vertex_buffer[(index*size)+8]) + "{:02x}".format(vertex_buffer[(index*size)+9]) + "{:02x}".format(vertex_buffer[(index*size)+10]) + "{:02x}".format(vertex_buffer[(index*size)+11])
    #print(str(temp))
    vertex3 = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6))
    


    obj_file.write("v " + vertex1 + " " +vertex2 +" " + vertex3 + "\n" )

#Write UV

for index in range(int( len(vertex_buffer) / (len(vertex_buffer)/vertex_count) ) ):
    temp = "{:02x}".format(vertex_buffer[(index*size)+44]) + "{:02x}".format(vertex_buffer[(index*size)+45]) + "{:02x}".format(vertex_buffer[(index*size)+46]) + "{:02x}".format(vertex_buffer[(index*size)+47])
    #print(str(temp))
    u = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6))
    
    temp = "{:02x}".format(vertex_buffer[(index*size)+48]) + "{:02x}".format(vertex_buffer[(index*size)+49]) + "{:02x}".format(vertex_buffer[(index*size)+50]) + "{:02x}".format(vertex_buffer[(index*size)+51])
    #print(str(temp))
    v = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6))
    

    


    obj_file.write("vt " + u + " " +  v+ "\n" )



#Write Normals
for index in range(int( len(vertex_buffer) / (len(vertex_buffer)/vertex_count) ) ):
    temp = "{:02x}".format(vertex_buffer[(index*size)+12]) + "{:02x}".format(vertex_buffer[(index*size)+13]) + "{:02x}".format(vertex_buffer[(index*size)+14]) + "{:02x}".format(vertex_buffer[(index*size)+15])
    #print(str(temp))
    vertex1 = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6)*-1)
    
    temp = "{:02x}".format(vertex_buffer[(index*size)+16]) + "{:02x}".format(vertex_buffer[(index*size)+17]) + "{:02x}".format(vertex_buffer[(index*size)+18]) + "{:02x}".format(vertex_buffer[(index*size)+19])
    #print(str(temp))
    vertex2 = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6)*-1)
    
    temp = "{:02x}".format(vertex_buffer[(index*size)+20]) + "{:02x}".format(vertex_buffer[(index*size)+21]) + "{:02x}".format(vertex_buffer[(index*size)+22]) + "{:02x}".format(vertex_buffer[(index*size)+23])
    #print(str(temp))
    vertex3 = str(round(struct.unpack('f', bytes.fromhex(temp))[0],6)*-1)
    


    obj_file.write("vn " + vertex1 + " " +vertex2 +" " + vertex3 + "\n" )


#Write Faces
obj_file.write("usemtl " + uv_material_name +"\n")
obj_file.write("g " + mesh_name +"_0\n")

for index in range(int(len(index_buffer)/3)):
    face1 = str(index_buffer[index*3]) + "/" + str(index_buffer[index*3]) + "/" + str(index_buffer[index*3]) + " "
    face2 = str(index_buffer[(index*3)+1]) + "/" + str(index_buffer[(index*3)+1]) + "/" + str(index_buffer[(index*3)+1]) + " "
    face3 = str(index_buffer[(index*3)+2]) + "/" + str(index_buffer[(index*3)+2]) + "/" + str(index_buffer[(index*3)+2]) + " "
    obj_file.write("f " + face3 + face2 + face1 + "\n" )



    ###########################################
    #Create MTL File (.OBJ Material File)

mtl_file = open(mtl_filename, "w+")


mtl_file.write("# Blender MTL File: 'None'\n")
mtl_file.write("# Material Count: 1\n")

mtl_file.write("newmtl "+ uv_material_name +"\n")
mtl_file.write("Ns 225.000000\n")
mtl_file.write("Ka 1.000000 1.000000 1.000000\n")
mtl_file.write("Kd 0.800000 0.800000 0.800000\n")
mtl_file.write("Ks 0.500000 0.500000 0.500000\n")
mtl_file.write("Ke 0.000000 0.000000 0.000000\n")
mtl_file.write("Ni 1.450000\n")
mtl_file.write("d 1.000000\n")
mtl_file.write("illum 2\n")
mtl_file.write("map_Kd Earth_Full_DarkerSea.png\n")
mtl_file.write("map_Ke Earth_Emission_Full_2.png\n")