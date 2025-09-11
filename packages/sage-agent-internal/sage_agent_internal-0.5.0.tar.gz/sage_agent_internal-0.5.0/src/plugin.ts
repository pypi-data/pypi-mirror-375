import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import {
  ICommandPalette,
  IThemeManager,
  IToolbarWidgetRegistry,
  WidgetTracker
} from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ToolService } from './Services/ToolService';
import { ConfigService } from './Config/ConfigService';
import { NotebookTools } from './Notebook/NotebookTools';
import { ActionHistory } from './Chat/ActionHistory';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { CellTrackingService } from './CellTrackingService';
import { TrackingIDUtility } from './TrackingIDUtility';
import { NotebookChatContainer } from './Notebook/NotebookChatContainer';
import { NotebookContextManager } from './Notebook/NotebookContextManager';
import { addIcon } from '@jupyterlab/ui-components';
import { ContextCellHighlighter } from './Chat/ChatContextMenu/ContextCellHighlighter';
import { AppStateService } from './AppState';
import { NotebookSettingsContainer } from './NotebookSettingsContainer';
import { Widget } from '@lumino/widgets';
import { PlanStateDisplay } from './Components/PlanStateDisplay';
import { WaitingUserReplyBoxManager } from './Notebook/WaitingUserReplyBoxManager';
import { registerCommands } from './commands';
import { registerEvalCommands } from './eval_commands';
import { NotebookDiffTools } from './Notebook/NotebookDiffTools';
import { ListModel } from '@jupyterlab/extensionmanager';
import { CachingService, SETTING_KEYS } from './utils/caching';
import { StateDBCachingService } from './utils/stateDBCaching';
import { KernelUtils } from './utils/kernelUtils';
import { DatabaseMetadataCache } from './Services/DatabaseMetadataCache';
import { ContextCacheService } from './Chat/ChatContextMenu/ContextCacheService';
import { KernelExecutionListener } from './Chat/ChatContextMenu/KernelExecutionListener';
import { IStateDB } from '@jupyterlab/statedb';
import { v4 as uuidv4 } from 'uuid';
import { SnippetCreationWidget } from './Components/SnippetCreationWidget';
import { TabCompletionService } from './Services/TabCompletionService';
import { CompletionManager } from './Services/CompletionManager';
import { DiffNavigationWidget } from './Components/DiffNavigationWidget';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { timeout } from './utils';
import { LLMStateDisplay } from './Components/LLMStateDisplay';
import { activateSage } from './activateSage';
import { 
  getGlobalSnippetCreationWidget,
  getGlobalDiffNavigationWidget,
  setGlobalSnippetCreationWidget,
  setGlobalDiffNavigationWidget 
} from './globalWidgets';

const THEME_FLAG_KEY = 'darkThemeApplied';
/**
 * Initialization data for the sage-ai extension
 */
export const plugin: JupyterFrontEndPlugin<void> = {
  id: 'sage-agent-internal:plugin',
  description: 'Sage AI - Your AI Data Partner',
  autoStart: true,
  requires: [
    INotebookTracker,
    ICommandPalette,
    IThemeManager,
    IStateDB,
    IDocumentManager
  ],
  optional: [ISettingRegistry, IToolbarWidgetRegistry],
  activate: (
    app: JupyterFrontEnd,
    notebooks: INotebookTracker,
    palette: ICommandPalette,
    themeManager: IThemeManager,
    db: IStateDB,
    documentManager: IDocumentManager,
    settingRegistry: ISettingRegistry | null,
    toolbarRegistry: IToolbarWidgetRegistry | null
  ) => {
    console.log('JupyterLab extension sage-agent-internal is activated!');
    activateSage(
      app,
      notebooks,
      palette,
      themeManager,
      db,
      documentManager,
      settingRegistry,
      toolbarRegistry,
      plugin
    );
  },
  deactivate: () => {
    console.log('JupyterLab extension sage-agent-internal is deactivated!');

    // Cleanup snippet creation widget
    const snippetWidget = getGlobalSnippetCreationWidget();
    if (snippetWidget && !snippetWidget.isDisposed) {
      snippetWidget.dispose();
      setGlobalSnippetCreationWidget(undefined);
    }

    // Cleanup diff navigation widget
    const diffWidget = getGlobalDiffNavigationWidget();
    if (diffWidget && !diffWidget.isDisposed) {
      // Remove from DOM (could be attached to notebook or document.body)
      if (diffWidget.node.parentNode) {
        diffWidget.node.parentNode.removeChild(diffWidget.node);
      }
      diffWidget.dispose();
      setGlobalDiffNavigationWidget(undefined);
    }

    // Cleanup kernel execution listener
    const kernelExecutionListener = KernelExecutionListener.getInstance();
    kernelExecutionListener.dispose();

    // Cleanup theme detection
    NotebookDiffTools.cleanupThemeDetection();
  }
};
