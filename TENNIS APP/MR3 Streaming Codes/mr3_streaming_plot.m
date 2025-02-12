function varargout = mr3_streaming_plot(varargin)
% MR3_STREAMING_PLOT MATLAB code for mr3_streaming_plot.fig
%      MR3_STREAMING_PLOT, by itself, creates a new MR3_STREAMING_PLOT or raises the existing
%      singleton*.
%
%      H = MR3_STREAMING_PLOT returns the handle to a new MR3_STREAMING_PLOT or the handle to
%      the existing singleton*.
%
%      MR3_STREAMING_PLOT('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in MR3_STREAMING_PLOT.M with the given input arguments.
%
%      MR3_STREAMING_PLOT('Property','Value',...) creates a new MR3_STREAMING_PLOT or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before mr3_streaming_plot_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to mr3_streaming_plot_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help mr3_streaming_plot

% Last Modified by GUIDE v2.5 18-Oct-2016 15:57:36

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @mr3_streaming_plot_OpeningFcn, ...
                   'gui_OutputFcn',  @mr3_streaming_plot_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before mr3_streaming_plot is made visible.
function mr3_streaming_plot_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to mr3_streaming_plot (see VARARGIN)

% Choose default command line output for mr3_streaming_plot
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

handles.server = '';

% UIWAIT makes mr3_streaming_plot wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = mr3_streaming_plot_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in connectBtn.
function connectBtn_Callback(hObject, eventdata, handles)
% hObject    handle to connectBtn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


a = exist('webread');

if a == 0
    errordlg('webread() missing. (Matlab R2014b+ required.)','Version Error');
    return;
end


handles.server_url = strcat('http://', get(handles.serverTxt, 'String'));
handles.headers_url = strcat(handles.server_url,'/headers');
handles.samples_url = strcat(handles.server_url,'/samples');
handles.disable_url = strcat(handles.server_url,'/disable');
handles.enable_url = strcat(handles.server_url,'/enable');

%load the headers to get the available data channels
handles.headerdata = readStream(handles.headers_url);

if ~isstruct(handles.headerdata)
    errordlg('Server not found.  Make sure MR3 is measuring and HTTP Streaming is enabled','Connection Error');
    return;
end

set(handles.channel, 'enable', 'on');


handles.channelnames = {};
handles.channel_indices = {};
handles.sample_rates = {};
handles.channel_types = {};

% store name, type and index for each channel
for n=1:length(handles.headerdata.headers)
   header = handles.headerdata.headers(n);   
   handles.channel_names{n} = strcat(header.name, ' (', header.type, ')');
   handles.channel_indices{n} = header.index;
   handles.sample_rates{n} = header.samplerate;
   handles.channel_types{n} = header.type;
end

% fill channels list
set(handles.channel, 'String', strvcat(handles.channel_names));

% enable start button
set(handles.startBtn, 'enable', 'on');

% save handles data
guidata(hObject,handles)




% --- Executes on selection change in channel.
function channel_Callback(hObject, eventdata, handles)
% hObject    handle to channel (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns channel contents as cell array
%        contents{get(hObject,'Value')} returns selected item from channel


% --- Executes during object creation, after setting all properties.
function channel_CreateFcn(hObject, eventdata, handles)
% hObject    handle to channel (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


function size = type_to_size(type)
if isempty(strfind(type,'vector3'))
    size = 1;
else
    size = 3;
end
 

% --- Executes on button press in startBtn.
function startBtn_Callback(hObject, eventdata, handles)
% hObject    handle to startBtn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% get selected index
handles.channel_index = handles.channel_indices{get(handles.channel, 'Value')};

% get sample rate for selected channel
handles.sample_rate = handles.sample_rates{get(handles.channel, 'Value')};

% get channel type
handles.channel_type = handles.channel_types{get(handles.channel, 'Value')};

% enable correct axes(s)
if strcmp(handles.channel_type, 'vector3.accel') || strcmp(handles.channel_type, 'vector3.rot')
    set(handles.plot, 'Visible', 'off');
    set(handles.subplot1, 'Visible', 'on');
    set(handles.subplot2, 'Visible', 'on');
    set(handles.subplot3, 'Visible', 'on');
else    
    set(handles.plot, 'Visible', 'on');
    set(handles.subplot1, 'Visible', 'off');
    set(handles.subplot2, 'Visible', 'off');
    set(handles.subplot3, 'Visible', 'off');
end

% get channel size (1 or 3 elements)
handles.channel_size = type_to_size(handles.channel_type);

% disable all channels
writeStream(strcat(handles.disable_url,'/all'));

% enable selected channel
writeStream(strcat(handles.enable_url,'/',num2str(handles.channel_index)));

% disable start button
set(handles.startBtn, 'enable', 'off');

% enable stop button
set(handles.stopBtn, 'enable', 'on');

% set plot size to 10 seconds
handles.plot_size = 10 * handles.sample_rate;

% clear plot data
handles.plot_data = zeros(handles.plot_size,handles.channel_size);

% clear plot index
handles.plot_index = 1;

% save handles data
guidata(hObject,handles);

% create timer
handles.timer = timer;
set(handles.timer, 'BusyMode', 'drop');
set(handles.timer, 'ExecutionMode', 'fixedRate');
set(handles.timer, 'Period', 0.2);
set(handles.timer, 'TimerFcn', {@timer_callback_fcn, handles.output});

% save handles data
guidata(hObject,handles);

start(handles.timer);



function timer_callback_fcn(hObject, eventdata, hFigure)

% get handles fata
handles = guidata(hFigure);

% read new samples
data = readStream(handles.samples_url);

if isstruct(data) 

    for n = 1:length(data.channels)
        if data.channels(n).index == handles.channel_index

            samples = data.channels(n).samples;
            component_index = 1;

            for s = 1:1:length(samples)
                handles.plot_data(handles.plot_index, component_index) = samples(s);

                component_index = component_index + 1;
                if component_index > handles.channel_size
                    component_index = 1;
                    handles.plot_index = handles.plot_index + 1;
                    if handles.plot_index > handles.plot_size
                        handles.plot_index = 1;
                    end
                end
            end
        end
    end

    %update plot
    if strcmp(handles.channel_type, 'vector3.pos')
        scatter3(handles.plot, handles.plot_data(1:end,1), handles.plot_data(1:end,3), handles.plot_data(1:end,2));    
    elseif strcmp(handles.channel_type, 'vector3.accel') || strcmp(handles.channel_type, 'vector3.rot')
        x = 1:1:handles.plot_size;
        plot(handles.subplot1, x, handles.plot_data(1:end,1), 'r');
        plot(handles.subplot2, x, handles.plot_data(1:end,2), 'g');
        plot(handles.subplot3, x, handles.plot_data(1:end,3), 'b');  
    else
        x = 1:1:handles.plot_size;
        plot(handles.plot, x, handles.plot_data(1:end,1), 'r');

    end
    % save handles data
    guidata(hFigure,handles);
end %isstruct(data)




% --- Executes on button press in stopBtn.
function stopBtn_Callback(hObject, eventdata, handles)
% hObject    handle to stopBtn (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB

% handles    structure with handles and user data (see GUIDATA)

% stop timer
stop(handles.timer);

% disable stop button
set(handles.stopBtn, 'enable', 'off');

% enable start button
set(handles.startBtn, 'enable', 'on');

%clear plots
cla(handles.plot);
cla(handles.subplot1);
cla(handles.subplot2);
cla(handles.subplot3);


function serverTxt_Callback(hObject, eventdata, handles)
% hObject    handle to serverTxt (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of serverTxt as text
%        str2double(get(hObject,'String')) returns contents of serverTxt as a double


% --- Executes during object creation, after setting all properties.
function serverTxt_CreateFcn(hObject, eventdata, handles)
% hObject    handle to serverTxt (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function data = readStream(url)
try 
data = webread(url, weboptions('ContentType','json','Timeout',5));
catch
    data = [];
end

function writeStream(url)
try 
webread(url, weboptions('ContentType','json','Timeout',5));
catch 
    errordlg('Server not found.  Make sure MR3 is measuring and HTTP Streaming is enabled','Connection Error');
end

% --- Executes during object creation, after setting all properties.
function startBtn_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pushbutton4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% --- Executes during object creation, after setting all properties.
function stopBtn_CreateFcn(hObject, eventdata, handles)
% hObject    handle to pushbutton4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
