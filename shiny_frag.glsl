uniform float t;

uniform sampler2D sky;
uniform vec4 bgcolor;

varying vec3 normal;
varying vec4 pos;

float Dx(in float x, in float y, in float t)
{
    return 2*sin(10*(t - length(vec2(x, y)))) * x;
}

float Dy(in float x, in float y, in float t)
{
    return 2*sin(10*(t - length(vec2(x, y)))) * y;
}

float fog(in vec3 pos)
{
	float r = length(pos);
	
	if (r > 5.0)
	{
		return 0.0;
	}
	else
	{
		return (5.0 - r) / 5.0;
	}
}

void main()
{
   // ref: http://www.reindelsoftware.com/Documents/Mapping/Mapping.html
   vec3 V = gl_ModelViewMatrix*pos;
   vec4 sky_rgba;
   float alpha;
 
   // Calculate normal at every pixel:

   vec3 dx = vec3(1, 0, Dx(pos.x, pos.y, t));
   vec3 dy = vec3(0, 1, Dy(pos.x, pos.y, t));
   vec3 norm_calc = gl_NormalMatrix*normalize(cross(dx, dy));
     
     
   float d = dot(V, norm_calc);
   vec3 R = V - 2*d*norm_calc;
   
   float m = 2 * sqrt(pow(R.x, 2.0) + pow(R.y, 2.0) + pow(R.z + 1, 2.0));
   float u = R.x / m + 0.5;
   float v = R.y / m + 0.5;
   
   sky_rgba = texture2D(sky, vec2(u, v));
   
   alpha = fog(pos);
   //gl_FragColor = gl_Color;
   gl_FragColor =  vec4(alpha * vec3(sky_rgba) + (1 - alpha) * vec3(bgcolor), 1.0);
}
