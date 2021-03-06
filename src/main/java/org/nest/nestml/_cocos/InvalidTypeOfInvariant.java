/*
 * Copyright (c)  RWTH Aachen. All rights reserved.
 *
 * http://www.se-rwth.de/
 */
package org.nest.nestml._cocos;

import de.se_rwth.commons.logging.Log;
import org.nest.nestml._ast.ASTDeclaration;
import org.nest.nestml._symboltable.typechecking.Either;
import org.nest.nestml._symboltable.predefined.PredefinedTypes;
import org.nest.nestml._symboltable.symbols.TypeSymbol;
import org.nest.utils.AstUtils;

/**
 * Invariants expressions must be of the type boolea.
 *
 * @author ppen, plotnikov
 */
class InvalidTypeOfInvariant implements NESTMLASTDeclarationCoCo {


  public void check(final ASTDeclaration alias) {
    if (alias.getInvariant().isPresent()) {
      final Either<TypeSymbol, String> expressionType = alias.getInvariant().get().getType();

      if (expressionType.isValue()) {

        if (!expressionType.getValue().equals(PredefinedTypes.getBooleanType())) {
          final String msg = NestmlErrorStrings.getErrorMsgInvariantMustBeBoolean(this,expressionType.toString());

          Log.error(msg, alias.getInvariant().get().get_SourcePositionStart());
        }
      }
      else {
        final String msg = NestmlErrorStrings.getErrorMsgCannotComputeType(this,
                AstUtils.toString(alias.getInvariant().get()));

        Log.warn(msg,alias.getInvariant().get().get_SourcePositionStart());
      }

    }

  }


}
