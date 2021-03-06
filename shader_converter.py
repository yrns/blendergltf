import re

import gpu


def vs_to_130(data):
    data['attributes'].append({'varname': 'bl_Vertex', 'type': gpu.CD_ORCO, 'datatype': gpu.GPU_DATA_3F})
    data['attributes'].append({'varname': 'bl_Normal', 'type': -1, 'datatype': gpu.GPU_DATA_3F})
    src = data['vertex']
    src = '#version 130\nin vec4 bl_Vertex;\nin vec3 bl_Normal;\nuniform mat4 bl_ModelViewMatrix;\nuniform mat4 bl_ProjectionMatrix;\nuniform mat3 bl_NormalMatrix;\n' + src
    src = re.sub(r'#ifdef USE_OPENSUBDIV([^#]*)#endif', '', src)
    src = re.sub(r'#ifndef USE_OPENSUBDIV([^#]*)#endif', r'\1', src)
    src = re.sub(r'#ifdef CLIP_WORKAROUND(.*?)#endif', '', src, 0, re.DOTALL)
    src = re.sub(r'\bvarying\b', 'out', src)
    src = re.sub(r'\bgl_(?!Position)(.*?)\b', r'bl_\1', src)

    data['vertex'] = src


def fs_to_130(data):
    src = data['fragment']
    src = '#version 130\nout vec4 frag_color;\nuniform mat4 bl_ProjectionMatrix;\nuniform mat4 bl_ModelViewMatrix;\nuniform mat4 bl_ModelViewMatrixInverse;\nuniform mat3 bl_NormalMatrix;\nuniform mat4 bl_ProjectionMatrixInverse;\n' + src
    src = re.sub(r'\bvarying\b', 'in', src)
    src = re.sub(r'\bgl_FragColor\b', 'frag_color', src)
    src = re.sub(r'\bgl_(?!FrontFacing)(.*?)\b', r'bl_\1', src)

    # Cannot support node_bsdf functions without resolving use of gl_Light
    src = re.sub(r'void node_((bsdf)|(subsurface))_.*?^}', '', src, 0, re.DOTALL|re.MULTILINE)

    data['fragment'] = src.replace('\r\r\n', '')


def vs_to_web(data):
    src = data['vertex']

    precision_block = '\n'
    for data_type in ('float','int'):
        precision_block += 'precision mediump {};\n'.format(data_type)

    src = src.replace('#version 130', '#version 100\n' + precision_block)
    src = re.sub(r'\bin\b', 'attribute', src)
    src = re.sub(r'\bout\b', 'varying', src)

    data['vertex'] = src


def fs_to_web(data):
    src = data['fragment']

    precision_block = '\n'
    for data_type in ('float','int'):
        precision_block += 'precision mediump {};\n'.format(data_type)

    src = src.replace('#version 130', '#version 100\n#extension GL_OES_standard_derivatives: enable\n' + precision_block)
    src = re.sub(r'\bin\b', 'varying', src)
    src = src.replace('out vec4 frag_color;\n', '')
    src = re.sub(r'\bfrag_color\b', 'gl_FragColor', src)

    #TODO: This should be fixed in Blender
    src = src.replace('blend = (normalize(vec).z + 1)', 'blend = (normalize(vec).z + 1.0)')

    #TODO: This likely breaks shadows
    src = src.replace('sampler2DShadow', 'sampler2D')
    src = src.replace('shadow2DProj', 'texture2DProj')

    data['fragment'] = src


def to_130(data):
    vs_to_130(data)
    fs_to_130(data)


def to_web(data):
    to_130(data)
    vs_to_web(data)
    fs_to_web(data)
