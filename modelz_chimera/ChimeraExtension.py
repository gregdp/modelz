from  chimera.extension import EMO, manager

# -----------------------------------------------------------------------------
#
class ModelZ_Dialog_EMO ( EMO ):

  def name(self):
    return 'ModelZ'
  def description(self):
    return self.categoryDescriptions()['Volume Data']
  def categories(self):
    return self.categoryDescriptions().keys()
  def categoryDescriptions(self):
    # since we want to use specialized descriptions for certain categories...
    return {
      'Volume Data': 'Calculate Z-scores for map & model',
    }
  def icon(self):
    return None #self.path('volseg.png')
  def activate(self):
    # self.module('volumedialog').show_volume_dialog()
    d = self.module('modelz').show_dialog()
    return None

# -----------------------------------------------------------------------------
# Register dialogs and menu entry.
#
manager.registerExtension ( ModelZ_Dialog_EMO ( __file__ ) )

