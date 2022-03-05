import sys
import struct
import os

major = 1
minor = 0


obj_filename = sys.argv[1]
mtl_filename = obj_filename.split(".")[0] + ".mtl"

obj_file = open(obj_filename, 'r')
mtl_file = open(mtl_filename, 'r')

#Read the .OBJ and .MTL file
OBJ_LINES = obj_file.readlines()
MTL_LINES = mtl_file.readlines()


#make the output director
build_dir = obj_filename.split(".")[0] + "_recompiled"
try:
    os.mkdir(build_dir)
except:
    print("Directory Already Created")
#Open new file to write asset to
asset_file = build_dir + "\\UABE_Generated_Asset.txt"
asset_file = open(asset_file, 'w')

fail_flag = 0


vertex_count = 0
index_count = 0
mesh_name = ""
print("Solar Smash Unity Tools Asset Packer v." + str(major) + "." + str(minor))


############################################
#Extract Material Data

material_count = 0
material_name = ""
kd_map = ""
ke_map = ""
ks_map = ""

for line in MTL_LINES:
    if "Material Count" in line:
        material_count = int(line.split(":")[1].strip())

    elif "newmtl" in line:
        material_name = line.split()[1].strip()

    elif "map_Kd" in line:
        kd_map = line.split()[1]
        print("Found Kd Map")

    elif "map_Ke" in line:
        ke_map = line.split()[1]
        print("Found Ke Map")

    elif "map_Ks" in line:
        ks_map = line.split()[1]
        print("Found Ks Map")


if (material_name != "") and (kd_map != "") and (ke_map != "") and (ks_map != ""):
    print("Material File Accepted")
else:
    print("Incompatable Material File")
    fail_flag = 1



############################################
#Extract Object Data

vertex_buffer = []
normal_buffer = []
uv_buffer = []
vertex_index_buffer = []
normal_index_buffer = []
uv_index_buffer = []

vertex_count = 0
uv_count = 0
normal_count = 0
face_count = 0

for line in OBJ_LINES:

    #Extract Vertex
    if line.split()[0] == "v":
        x_float = float(line.split()[1].strip())
        y_float = float(line.split()[2].strip())
        z_float = float(line.split()[3].strip())

        x_bytes = bytearray(struct.pack("f", x_float))
        y_bytes = bytearray(struct.pack("f", y_float))
        z_bytes = bytearray(struct.pack("f", z_float))

        x_packed = [x_bytes[3],x_bytes[2],x_bytes[1],x_bytes[0]]
        y_packed = [y_bytes[3],y_bytes[2],y_bytes[1],y_bytes[0]]
        z_packed = [z_bytes[3],z_bytes[2],z_bytes[1],z_bytes[0]]

        vertex_buffer.append([x_packed,y_packed,z_packed])
        vertex_count+=1

     #Extract UV Map
    elif line.split()[0] == "vt":
        u_float = float(line.split()[1].strip())
        v_float = float(line.split()[2].strip())


        u_bytes = bytearray(struct.pack("f", u_float))
        v_bytes = bytearray(struct.pack("f", v_float))


        uv_buffer.append([u_bytes,v_bytes])
        uv_count+=1
       
    #Extract normals
    elif line.split()[0] == "vn":
        x_float = float(line.split()[1].strip())
        y_float = float(line.split()[2].strip())
        z_float = float(line.split()[3].strip())

        x_bytes = bytearray(struct.pack("f", x_float))
        y_bytes = bytearray(struct.pack("f", y_float))
        z_bytes = bytearray(struct.pack("f", z_float))

        x_packed = [x_bytes[3],x_bytes[2],x_bytes[1],x_bytes[0]]
        y_packed = [y_bytes[3],y_bytes[2],y_bytes[1],y_bytes[0]]
        z_packed = [z_bytes[3],z_bytes[2],z_bytes[1],z_bytes[0]]

        normal_buffer.append([x_packed,y_packed,z_packed])
        normal_count+=1

    #Extract faces
    elif line.split()[0] == "f":

        #Faces are stored in reverse order for some reason
        face_pointer_1 = line.split()[3].strip().split("/")
        face_pointer_2 = line.split()[2].strip().split("/")
        face_pointer_3 = line.split()[1].strip().split("/")

        vertex_index_buffer.append( [ int(face_pointer_1[0]), int(face_pointer_2[0]), int(face_pointer_3[0]) ])
        uv_index_buffer.append( [ int(face_pointer_1[1]), int(face_pointer_2[1]), int(face_pointer_3[1]) ])
        normal_index_buffer.append( [ int(face_pointer_1[2]), int(face_pointer_2[2]), int(face_pointer_3[2]) ])
        face_count+=1



print("Vertex Count: " + str(vertex_count))
print("UV Count: " + str(uv_count))
print("Normal Count: " + str(normal_count))
print("Face Count: " + str(face_count))

index_master = ""

if (vertex_count >= uv_count) and (vertex_count >= normal_count):
    print("Using Vertex as Index Master")
    index_master = 0
    asset_vertex_count = vertex_count

elif (uv_count >= vertex_count) and (uv_count >= normal_count):
    print("Using UV as Index Master")
    index_master = 1
    asset_vertex_count = uv_count

elif (normal_count >= vertex_count) and (normal_count >= uv_count):
    print("Using Normal as Index Master")    
    index_master = 2
    asset_vertex_count = normal_count


#The size of Solar Smash Vertex Packets
asset_vertex_buffer_size = asset_vertex_count * 52
asset_index_buffer_size = face_count * 6

print("Packing Asset File...", end='')


    ###########################################
    #Build UABE Asset 

asset_file.write("0 Mesh Base\n")
asset_file.write(' 1 string m_Name = "Earth"\n')
asset_file.write(" 0 vector m_SubMeshes\n")
asset_file.write("  1 Array Array (1 items)\n")
asset_file.write("   0 int size = 1\n")
asset_file.write("   [0]\n")
asset_file.write("    0 SubMesh data\n")
asset_file.write("     0 unsigned int firstByte = 0\n")
asset_file.write("     0 unsigned int indexCount = " + str(face_count*3) + "\n")
asset_file.write("     0 int topology = 0\n")
asset_file.write("     0 unsigned int baseVertex = 0\n")
asset_file.write("     0 unsigned int firstVertex = 0\n")
asset_file.write("     0 unsigned int vertexCount = " + str(asset_vertex_count) + "\n")
asset_file.write("     0 AABB localAABB\n")
asset_file.write("      0 Vector3f m_Center\n")
asset_file.write("       0 float x = 0\n")
asset_file.write("       0 float y = 0\n")
asset_file.write("       0 float z = 0\n")
asset_file.write("      0 Vector3f m_Extent\n")
asset_file.write("       0 float x = 15.036438\n")
asset_file.write("       0 float y = 15.036438\n")
asset_file.write("       0 float z = 15.03644\n")
asset_file.write(" 0 BlendShapeData m_Shapes\n")
asset_file.write("  0 vector vertices\n")
asset_file.write("   1 Array Array (0 items)\n")
asset_file.write("    0 int size = 0\n")
asset_file.write("  0 vector shapes\n")
asset_file.write("   1 Array Array (0 items)\n")
asset_file.write("    0 int size = 0\n")
asset_file.write("  0 vector channels\n")
asset_file.write("   1 Array Array (0 items)\n")
asset_file.write("    0 int size = 0\n")
asset_file.write("  0 vector fullWeights\n")
asset_file.write("   1 Array Array (0 items)\n")
asset_file.write("    0 int size = 0\n")
asset_file.write(" 0 vector m_BindPose\n")
asset_file.write("  1 Array Array (0 items)\n")
asset_file.write("   0 int size = 0\n")
asset_file.write(" 0 vector m_BoneNameHashes\n")
asset_file.write("  1 Array Array (0 items)\n")
asset_file.write("   0 int size = 0\n")
asset_file.write(" 0 unsigned int m_RootBoneNameHash = 0\n")
asset_file.write(" 0 vector m_BonesAABB\n")
asset_file.write("  1 Array Array (0 items)\n")
asset_file.write("   0 int size = 0\n")
asset_file.write(" 0 VariableBoneCountWeights m_VariableBoneCountWeights\n")
asset_file.write("  0 vector m_Data\n")
asset_file.write("   1 Array Array (0 items)\n")
asset_file.write("    0 int size = 0\n")
asset_file.write(" 0 UInt8 m_MeshCompression = 0\n")
asset_file.write(" 0 bool m_IsReadable = true\n")
asset_file.write(" 0 bool m_KeepVertices = false\n")
asset_file.write(" 1 bool m_KeepIndices = false\n")
asset_file.write(" 0 int m_IndexFormat = 0\n")
asset_file.write(" 0 vector m_IndexBuffer\n")

###########################################
#write Index Buffer
asset_file.write("  1 Array Array ("+ str(asset_index_buffer_size) + " items)\n")
asset_file.write("   0 int size = "+ str(asset_index_buffer_size) +"\n")

def int_to_byte(value):
    value = value - 1
    if value > 255:
        h = int(value/256)
        l = int(value%256)
        #print("LOW: " + str(l) + " HIGH: " + str(h))
        return [h,l]
    else:
        return [0,value]

#print(vertex_index_buffer)
face_byte= [0,0]
#Write the Index buffer
for position in range(face_count):
    
    for face in range(3):
        if index_master == 0:
            face_byte = int_to_byte(vertex_index_buffer[position][face])

        elif index_master == 1:
            face_byte = int_to_byte(uv_index_buffer[position][face])

        elif index_master == 2:
            face_byte = int_to_byte(normal_index_buffer[position][face])


        asset_file.write("   [" + str((position*6)+face*2) + "]\n")
        asset_file.write("    0 UInt8 data = " + str(int(face_byte[1])) + "\n")

        asset_file.write("   [" + str((position*6)+(face*2)+1) + "]\n")
        asset_file.write("    0 UInt8 data = " + str(int(face_byte[0])) + "\n")





asset_file.write(" 1 VertexData m_VertexData\n")
asset_file.write("  0 unsigned int m_VertexCount = 10349\n")
asset_file.write("  0 vector m_Channels\n")
asset_file.write("   1 Array Array (14 items)\n")
asset_file.write("    0 int size = 14\n")
asset_file.write("    [0]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 3\n")
asset_file.write("    [1]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 12\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 3\n")
asset_file.write("    [2]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 24\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 4\n")
asset_file.write("    [3]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 40\n")
asset_file.write("      0 UInt8 format = 2\n")
asset_file.write("      0 UInt8 dimension = 4\n")
asset_file.write("    [4]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 44\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 2\n")
asset_file.write("    [5]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [6]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [7]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [8]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [9]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [10]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [11]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [12]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")
asset_file.write("    [13]\n")
asset_file.write("     0 ChannelInfo data\n")
asset_file.write("      0 UInt8 stream = 0\n")
asset_file.write("      0 UInt8 offset = 0\n")
asset_file.write("      0 UInt8 format = 0\n")
asset_file.write("      0 UInt8 dimension = 0\n")

 ###########################################
#Write Vertex Buffer
position = 0





#Write Vertex Buffer Size
asset_file.write("  1 TypelessData m_DataSize ("+ str(asset_vertex_buffer_size) +" items)\n")
asset_file.write("   0 int size = "+ str(asset_vertex_buffer_size) +"\n")

#Write the vertex buffer
for position in range(asset_vertex_count):
    
    x_3d = vertex_buffer[position][0]
    y_3d = vertex_buffer[position][1]
    z_3d = vertex_buffer[position][2]

    u_uv = uv_buffer[position][0]
    v_uv = uv_buffer[position][1]
  

    x_normal = normal_buffer[position][0]
    y_normal = normal_buffer[position][1]
    z_normal = normal_buffer[position][2]

    #Write 3D data X
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(x_3d[i])) + "\n")        

    #Write 3D data Y
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+4+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(y_3d[i])) + "\n")      

    #Write 3D data Z
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+8+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(z_3d[i])) + "\n")      



    #Write Normal Data X
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+12+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(x_normal[i])) + "\n")   

    #Write Normal Data Y
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+16+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(y_normal[i])) + "\n")  

    #Write Normal Data Z
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+20+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(z_normal[i])) + "\n")                    



    #Write Unknow Channel
    for i in range(20):
        asset_file.write("   ["+ str((position*52)+24+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(0)) + "\n")     


    #write UV Channel U
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+44+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(u_uv[i])) + "\n")     

    #write UV Channel V
    for i in range(4):
        asset_file.write("   ["+ str((position*52)+48+i) +"]\n")
        asset_file.write("    0 UInt8 data = " + str(int(v_uv[i])) + "\n")     







asset_file.write(" 0 CompressedMesh m_CompressedMesh\n")
asset_file.write("  0 PackedBitVector m_Vertices\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 float m_Range = 0\n")
asset_file.write("   0 float m_Start = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_UV\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 float m_Range = 0\n")
asset_file.write("   0 float m_Start = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_Normals\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 float m_Range = 0\n")
asset_file.write("   0 float m_Start = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_Tangents\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 float m_Range = 0\n")
asset_file.write("   0 float m_Start = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_Weights\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_NormalSigns\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_TangentSigns\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_FloatColors\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 float m_Range = 0\n")
asset_file.write("   0 float m_Start = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_BoneIndices\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 PackedBitVector m_Triangles\n")
asset_file.write("   0 unsigned int m_NumItems = 0\n")
asset_file.write("   0 vector m_Data\n")
asset_file.write("    1 Array Array (0 items)\n")
asset_file.write("     0 int size = 0\n")
asset_file.write("   1 UInt8 m_BitSize = 0\n")
asset_file.write("  0 unsigned int m_UVInfo = 0\n")
asset_file.write(" 0 AABB m_LocalAABB\n")
asset_file.write("  0 Vector3f m_Center\n")
asset_file.write("   0 float x = 0\n")
asset_file.write("   0 float y = 0\n")
asset_file.write("   0 float z = 0\n")
asset_file.write("  0 Vector3f m_Extent\n")
asset_file.write("   0 float x = 15.036438\n")
asset_file.write("   0 float y = 15.036438\n")
asset_file.write("   0 float z = 15.03644\n")
asset_file.write(" 0 int m_MeshUsageFlags = 0\n")
asset_file.write(" 0 vector m_BakedConvexCollisionMesh\n")
asset_file.write("  1 Array Array (0 items)\n")
asset_file.write("   0 int size = 0\n")
asset_file.write(" 0 vector m_BakedTriangleCollisionMesh\n")
asset_file.write("  1 Array Array (0 items)\n")
asset_file.write("   0 int size = 0\n")
asset_file.write(" 0 float m_MeshMetrics[0] = 4259.5454\n")
asset_file.write(" 1 float m_MeshMetrics[1] = 1\n")
asset_file.write(" 0 StreamingInfo m_StreamData\n")
asset_file.write("  0 UInt64 offset = 0\n")
asset_file.write("  0 unsigned int size = 0\n")
asset_file.write('  1 string path = ""\n')


print("Done")