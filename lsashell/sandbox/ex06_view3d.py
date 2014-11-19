# -------------------------------------------------------------------------
#
# Copyright (c) 2009, IMB, RWTH Aachen.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in simvisage/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.simvisage.com/licenses/BSD.txt
#
# Thanks for using Simvisage open source!
#
# Created on Sep 8, 2011 by: matthias


import copy
import os
import string
import tempfile

from mayavi.core.api import \
    PipelineBase

from mayavi.core.ui.api import \
    MayaviScene, SceneEditor, MlabSceneModel

from traits.api import \
    HasTraits, Range, Instance, on_trait_change, \
    Property, cached_property, Button, \
    Int, Bool, File, Array, List, Float

from traitsui.api import \
    View, Item, Group, RangeEditor, \
    VGroup, HSplit, TreeEditor, \
    TreeNode, VSplit

from load_case_reader import \
    LCReader, LCReaderInfoCAD


FormingTask_tree_editor = TreeEditor(
    nodes=[
        TreeNode(node_for=[LCReader],
                 auto_open=False,
                 label='=LCReader',
                 children='',
                 ),
    ],
    hide_root=False,
    selected='data',
    editable=False,
)


class LSShellView(HasTraits):

    '''Crease pattern view.
    '''

    data = Instance(LCReader)
    '''Currently displayed data FormingTask step
    '''

    def _data_changed(self):
        self.fold_step = 0
        self.scene.mlab.clf()
        fig = self.scene.mlab.gcf()
        self.scene.mlab.figure(fig, fgcolor=(0, 0, 0),
                               bgcolor=(1, 1, 1))
        self.fold_step = 0

    root = Instance(LCReader)
    '''All FormingTask steps.
    '''

    scene = Instance(MlabSceneModel)

    def _scene_default(self):
        return MlabSceneModel()

    @on_trait_change('scene.activated')
    def scene_activated(self):
        '''
        Initialize all necessary pipelines
        '''
        self.update_lc_pipeline()

    fig = Property()
    '''Figure for 3D visualization.
    '''
    @cached_property
    def _get_fig(self):
        fig = self.scene.mlab.gcf()
        self.scene.mlab.figure(fig, fgcolor=(0, 0, 0),
                               bgcolor=(1, 1, 1))
        return fig

    lc_pipeline = Property(Instance(PipelineBase), depends_on='data')
    '''
    This Pipeline creates the raw construction. It builds all facets
    and connects the nodes like self.data.L describes it, but won't
    create the tubes.
    '''
    @cached_property
    def _get_lc_pipeline(self):

        # get the current constrain information

        print "constructing pipeline"

        state_data = lc_reader.read_state_data('LC6.txt')
        geo_data = lc_reader.read_geo_data('LC6.txt')
        return self.data.plot_sd(self.scene.mlab, geo_data,
                                 'mx', state_data, 10.0)

    @on_trait_change('data')
    def update_lc_pipeline(self):
        '''
        Update cp_pipeline for every new time_step
        '''
        # set new position of 3D Points
        self.scene.disable_render = True
        lcp = self.lc_pipeline  # @UnusedVariable
        self.scene.disable_render = False

    # The layout of the dialog created
    # The main view
    view1 = View(
        HSplit(VSplit(
               Group(Item('root',
                          editor=FormingTask_tree_editor,
                          resizable=True,
                          show_label=False),
                     label='Load case tree',
                     scrollable=True,
                     ),
               dock='tab'
               ),
               VGroup(
               Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                    show_label=False),
               label='3D View',
               dock='tab',
               ),
               ),
        dock='tab',
        resizable=True,
        width=1.0,
        height=1.0
    )

# =========================================================================
# Test Pattern
# =========================================================================

if __name__ == '__main__':

    from matresdev.db.simdb import \
        SimDB

    simdb = SimDB()

    dd = os.path.join(simdb.simdb_dir, 'simdata',
                      'input_data_barrelshell',
                      '2cm-feines-Netz',
                      )
    lc_reader = LCReaderInfoCAD(data_dir=dd)

    view = LSShellView(root=lc_reader, data=lc_reader)
    view.configure_traits()
