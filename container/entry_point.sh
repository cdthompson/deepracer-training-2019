#!/usr/bin/env bash

xhost +local:root
metacity --replace --no-composite &
mkdir -p $HOME/.devilspie
echo "(if (and
	  (is (window_property \"_NET_WM_WINDOW_TYPE\") \"_NET_WM_WINDOW_TYPE_NORMAL\")
	  (not (contains (window_property \"_NET_WM_STATE\") \"_NET_WM_STATE_MODAL\")))

	(begin
		(undecorate)
		(geometry \"2000x2000\")
		(maximize)
	)
)" >> $HOME/.devilspie/maximize.ds
devilspie&

join_paths="import sys,itertools; print(':'.join(set(itertools.chain.from_iterable(line.rstrip('\n').split(' ')[1].split(':') for line in sys.stdin if line.rstrip('\n')))))"
gazebo_ros_pkg_model_paths=`rospack plugins --attrib=gazebo_model_path gazebo_ros | python -c "${join_paths}"`
gazebo_ros_pkg_media_paths=`rospack plugins --attrib=gazebo_media_path gazebo_ros | python -c "${join_paths}"`
gazebo_ros_pkg_plugin_paths=`rospack plugins --attrib=plugin_path gazebo_ros | python -c "${join_paths}"`

export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:$gazebo_ros_pkg_model_paths
export GAZEBO_RESOURCE_PATH=$GAZEBO_RESOURCE_PATH:$gazebo_ros_pkg_media_paths
export GAZEBO_PLUGIN_PATH=$GAZEBO_PLUGIN_PATH:$gazebo_ros_pkg_plugin_paths

# If we have exited, write the exit code to a file.
GUI_TOOL_NAME=${@:$#}

# Set pwd to $Home folder to give guitools permission to create core dumps.
cd $HOME

while [ true ]; do
    echo "Sleeping before starting up the GUI tool"
    sleep 5
    ${@:$#}
    EXIT_CODE=$?
    TIMESTAMP=`date +%s`
    # To help crash cycle detection, append history of crashes to the crash file
    if [ $EXIT_CODE -ne 0 ]
    then
        echo "guitool-exit,$TIMESTAMP,$EXIT_CODE,$GUI_TOOL_NAME" >> $HOME/$GUI_TOOL_NAME.crash
    fi
done
