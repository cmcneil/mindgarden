uniform float t;
const float pi = 3.1415926535;

varying vec3 normal;
varying vec3 pos;

void main()
{  
   float rad = length(vec2(gl_Vertex.x, gl_Vertex.y));
   
   float z = 0.2*cos(10*(t - sqrt(pow(gl_Vertex.x, 2.0) + pow(gl_Vertex.y, 2.0))));
   vec3 world = vec3(gl_Vertex.x, gl_Vertex.y, z);
   
   
   // Change from [-5, 5] to [0, 1]
   float s = 2.0*((gl_Vertex.x + 5.0) / 10.0);
   float t = 2.0*((gl_Vertex.y + 5.0) / 10.0);
   //leaf_coord = vec2(s, t);
    
   pos = world; 
   gl_Position = gl_ModelViewProjectionMatrix * vec4(world,1.0);
   
}
